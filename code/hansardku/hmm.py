#!/usr/bin/env python3

from lxml import etree
import sys, os, csv, hashlib, base62, time, string, json, re
from xml2text import xml2text
from dropquotes import dropquotes
import itertools
from haiku import token_stream, poem_finder, Syllables, token_syllable_count
from pprint import pprint
from wsgiku import db, app, Document, Haiku, HaikuTrail

if __name__ == '__main__':
    def take(n, iterable):
        "Return first n items of the iterable as a list"
        return list(itertools.islice(iterable, n))

    def oneof(e, p):
        m = e.xpath(p)
        if not m:
            return
        matches = [xml2text(t).strip()for t in m]
        matches = [t for t in matches if t]
        if len(matches) == 0:
            return
        else:
            return matches[0]

    def killclass(et, cls, backto=None):
        elems = et.xpath('//*[@class="%s"]' % cls)
        for elem in elems:
            if backto is not None:
                elem = elem.xpath('ancestor::%s' % backto)[0]
            parent = elem.getparent()
            if parent is None:
                continue
            parent.remove(elem)

    def killelem(et, elem):
        elems = et.xpath('//%s' % elem)
        for elem in elems:
            parent = elem.getparent()
            if parent is None:
                continue
            parent.remove(elem)

    class TokenIssuer:
        def __init__(self):
            self.trails = {}

        def issue_for(self, t):
            if t not in self.trails:
                self.trails[t] = 0
            r = self.trails[t]
            self.trails[t] += 1
            return r

        def get_ngen(self, t):
            return self.trails[t]

        def make_trails(self):
            for trail in sorted(self.trails):
                trail = HaikuTrail(key=trail, length=self.trails[trail])
                db.session.add(trail)
                db.session.commit()

    issuer = TokenIssuer()

    def base62_sha1(s):
        digest = hashlib.sha1(s.encode('utf-8')).digest()
        return ''.join(base62.encode(v % 62) for v in digest[:8])

    class HaikuContext:
        def __init__(self, **kwargs):
            self.ctxt = kwargs

        def get(self, doc, poem):
            poem_uid = base62_sha1(':'.join(map(str, [
                doc.filename,
                doc.date,
                doc.parliament,
                doc.session,
                doc.period,
                doc.chamber,
                self.ctxt['talker_id'],
                poem])))
            r = self.ctxt.copy()
            r.update({
                'document_id' : doc.id,
                'poem' : poem,
                'poem_uid' : poem_uid,
                'poem_index' : issuer.issue_for('all'),
                'talker_index' : issuer.issue_for('talker=' + r['talker_id'])
                })
            return r

    def make_haiku_context(elem):
        name = oneof(elem, './talk.start/talker/name[@role="metadata"]')
        if name is None:
            name = oneof(elem, './talk.start/talker/name')
        if name.upper().find("PRESIDENT") != -1 or name.upper().find("SPEAKER") != -1:
            return None
        talker_id = oneof(elem, './talk.start/talker/name.id')
        if talker_id is None:
            return None
        talker_id = talker_id.upper()
        return HaikuContext(
            talker_id = talker_id,
            talker = name,
            party = oneof(elem, './talk.start/talker/party')
        )

    def make_document(info, et):
        return Document(
            filename = info['fname'],
            html_uri = info['uri'],
            xml_uri = info['xml_uri'],
            pdf_uri = info['pdf_uri'],
            date = oneof(et, '/hansard/session.header/date'),
            parliament = oneof(et, '/hansard/session.header/parliament.no'),
            session = oneof(et, '/hansard/session.header/session.no'),
            period = oneof(et, '/hansard/session.header/period.no'),
            chamber = oneof(et, '/hansard/session.header/chamber'),
        )

    def para_iter(e):
        killelem(e, "quote")
        killclass(e, "HPS-MemberIInterjecting", "p")
        killclass(e, "HPS-GeneralIInterjecting", "p")
        killclass(e, "HPS-MemberInterjecting", "p")
        killclass(e, "HPS-OfficeInterjecting", "p")
        killclass(e, "HPS-MinisterialTitles", "p")
        killclass(e, "HPS-Electorate", "p")
        killclass(e, "HPS-Time", "p")
        killclass(e, "HPS-MemberQuestion")
        killclass(e, "HPS-MemberContinuation")
        killclass(e, "HPS-MemberSpeech")
        killclass(e, "HPS-Small") # either a quote or something boring, like a motion

        def test_kill_quote(q):
            syllables = token_syllable_count(counter, q)
            # we don't want the inner of a quote making up an entire haiku; let's set a safe
            # level at ~ half the haiku, 9 syllables max
            if (syllables) >= 9:
                return True
            else:
                return False

        for elem in e.xpath('//talk.start/talker/../..'):
            # shouldn't pull in quotes (they're in quote/para)
            paras = elem.xpath('./talk.text/body/p | ./talk.start/para | ./para | ./talk.text/para')
            elem_ctxt = make_haiku_context(elem)
            if elem_ctxt is None:
                continue
            for para in paras:
                lines = [t.strip() for t in xml2text(para).splitlines()]
                lines = [item for sublist in map(lambda x: dropquotes(x, test_kill_quote), lines) for item in sublist ]
                yield elem_ctxt, lines

    db.create_all()
    db.session.commit()

    def make_haiku(info_file):
        def get_haiku(doc):
            for ctxt, para in para_iter(e):
                if ctxt.ctxt['party'] != 'AG': continue
                print(ctxt.ctxt['talker_id'], ctxt.ctxt['party'], ctxt.ctxt['talker'])
                with open('spkrs/%s.txt' % ctxt.ctxt['talker_id'], 'a') as fd:
                    fd.write('\n'.join(para))

        with open(info_file, 'r') as fd:
            info = json.load(fd)

        dname = os.path.dirname(info_file)
        xml_file = os.path.join(dname, info['fname'])
        with open(xml_file, 'rb') as fd:
            e = etree.parse(fd)

        doc = make_document(info, e)
        db.session.add(doc)
        db.session.commit()

        idx = 0
        written = set()
        outf = os.path.abspath('tmp/out.csv')
        with open(outf, 'w') as fd:
            w = csv.writer(fd)
            header = [ t.name for t in Haiku.__table__.columns ]
            get_haiku(doc)

        conn = db.session.connection()
        res = conn.execute('COPY %s FROM %%s CSV' % ('haiku'), (outf, ))
        db.session.commit()

        os.unlink(outf)
        return idx+1

    files = sys.argv[1:]
    runtime = 0

    haiku_pattern = [5, 7, 5]
    counter = Syllables()

    for i, info_file in enumerate(sys.argv[1:]):
        start_time = time.time()
        sys.stderr.write("%d/%d: %s... " % (i+1, len(files), info_file))
        sys.stderr.flush()
        doc_count = make_haiku(info_file)
        duration = time.time() - start_time
        if duration > 0:
            rate_s = ", %.1f haiku/s" % (doc_count/duration)
        runtime += duration
        time_per_file = runtime / (i + 1)
        eta = time_per_file * (len(files) - (i+1))
        eta_m = eta//60
        eta -= eta_m*60
        eta_h = eta_m//60
        eta_m -= eta_h*60
        sys.stderr.write("(%d haiku in %.2fs%s, ETA %dh%dm)\n" % (doc_count, duration, rate_s, eta_h, eta_m))
        sys.stderr.flush()
    print("%d haiku in the Hansard." % (issuer.get_ngen('all')))

    issuer.make_trails()

