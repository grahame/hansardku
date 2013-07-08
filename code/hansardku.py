#!/usr/bin/env python3

from lxml import etree
import sys, os, csv, hashlib, base62
from xml2text import xml2text
import itertools
from haiku import word_stream, poem_finder, Syllables
from pprint import pprint
from wsgiku import db, app, Document, Haiku

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

    class TokenIssuer:
        def __init__(self):
            self.ngen = 0

        def issue(self):
            r = self.ngen
            self.ngen += 1
            return r

    issuer = TokenIssuer()

    class HaikuContext:
        def __init__(self, **kwargs):
            self.ctxt = kwargs

        def get(self, doc, poem):
            dg = hashlib.sha1(':'.join(map(str, [
                doc.date,
                doc.parliament,
                doc.session,
                doc.period,
                doc.chamber,
                self.ctxt['talker_id'],
                poem])).encode('utf-8')).digest()
            poem_uid = ''.join(base62.encode(v % 62) for v in dg[:8])
            r = self.ctxt.copy()
            r.update({
                'id' : issuer.issue(),
                'document_id' : doc.id,
                'poem' : poem,
                'poem_uid' : poem_uid,
                })
            return r

    def make_haiku_context(elem):
        name = oneof(elem, './talk.start/talker/name[@role="metadata"]')
        if name is None:
            name = oneof(elem, './talk.start/talker/name')
        if name.upper().find("PRESIDENT") != -1 or name.upper().find("SPEAKER") != -1:
            return None
        return HaikuContext(
            talker_id = oneof(elem, './talk.start/talker/name.id'),
            talker = name,
            party = oneof(elem, './talk.start/talker/party')
        )

    def make_document(et):
        return Document(
            date = oneof(et, '/hansard/session.header/date'),
            parliament = oneof(et, '/hansard/session.header/parliament.no'),
            session = oneof(et, '/hansard/session.header/session.no'),
            period = oneof(et, '/hansard/session.header/period.no'),
            chamber = oneof(et, '/hansard/session.header/chamber'),
        )

    def para_iter(e):
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

        for elem in e.xpath('//talk.start/talker/../..'):
            # FIXME: borken.xml
            paras = elem.xpath('./talk.text/body/p | ./talk.start/para | ./para | ./talk.text/para')
            elem_ctxt = make_haiku_context(elem)
            if elem_ctxt is None:
                continue
            for para in paras:
                lines = [t.strip() for t in xml2text(para).splitlines()]
                yield elem_ctxt, lines

    haiku_pattern = [5, 7, 5]
    counter = Syllables()

    db.create_all()
    db.session.commit()

    def make_haiku(xml_file):
        def get_haiku(doc):
            for ctxt, para in para_iter(e):
                for poem in poem_finder(counter, word_stream(para), haiku_pattern):
                    yield ctxt.get(doc, '\n'.join(' '.join(line) for line in poem.get()))

        with open(xml_file, 'rb') as fd:
            e = etree.parse(fd)

        doc = make_document(e)
        db.session.add(doc)
        db.session.commit()

        outf = os.path.abspath('tmp/out.csv')
        with open(outf, 'w') as fd:
            w = csv.writer(fd)
            header = [ t.name for t in Haiku.__table__.columns ]
            uids = set()
            for idx, haiku in enumerate(t for t in get_haiku(doc)):
                uid = haiku['poem_uid']
                if uid in uids:
                    continue
                uids.add(uid)
                w.writerow([haiku[t] for t in header])

        conn = db.session.connection()
        res = conn.execute('COPY %s FROM %%s CSV' % ('haiku'), (outf, ))
        db.session.commit()

        os.unlink(outf)
        return idx+1

    files = sys.argv[1:]
    for i, xml_file in enumerate(sys.argv[1:]):
        sys.stderr.write("%d/%d: %s... " % (i+1, len(files), os.path.basename(xml_file)))
        sys.stderr.flush()
        doc_count = make_haiku(xml_file)
        sys.stderr.write("%d\n" % (doc_count))
        sys.stderr.flush()
    print("%d haiku in the Hansard." % (issuer.ngen))
