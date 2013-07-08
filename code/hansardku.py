#!/usr/bin/env python3

from lxml import etree
import sys, os, csv, hashlib, base62
from xml2text import xml2text
import itertools
from haiku import word_stream, poem_finder, Syllables
from pprint import pprint
from wsgiku import db, app, Haiku

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

    class HaikuWrapper:
        def __init__(self, **kwargs):
            self.doc = kwargs
            # generate UID
            dg = hashlib.sha1((self.doc['talker_id']+':'+self.doc['poem']).encode('utf-8')).digest()
            self.doc['poem_uid'] = ''.join(base62.encode(v % 62) for v in dg[:8])

        def get(self):
            return self.doc

    class HaikuContext:
        def __init__(self, doc):
            self.doc = doc

        def get(self, poem):
            return HaikuWrapper(id=issuer.issue(), poem=poem, **self.doc)

    class HaikuContextFactory:
        def __init__(self, et):
            self.session = {
                'date' : oneof(et, '/hansard/session.header/date'),
                'parliament' : oneof(et, '/hansard/session.header/parliament.no'),
                'session' : oneof(et, '/hansard/session.header/session.no'),
                'period' : oneof(et, '/hansard/session.header/period.no'),
                'chamber' : oneof(et, '/hansard/session.header/chamber'),
            }

        def create(self, elem):
            name = oneof(elem, './talk.start/talker/name[@role="metadata"]')
            if name is None:
                name = oneof(elem, './talk.start/talker/name')
            if name.upper().find("PRESIDENT") != -1 or name.upper().find("SPEAKER") != -1:
                return None
            doc = self.session.copy()
            doc.update({
                'talker_id' : oneof(elem, './talk.start/talker/name.id'),
                'talker' : name,
                'party' : oneof(elem, './talk.start/talker/party')
            })
            return HaikuContext(doc)

    def para_iter(xml_file):
        with open(xml_file, 'rb') as fd:
            e = etree.parse(fd)

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

        ctxt = HaikuContextFactory(e)
        for elem in e.xpath('//talk.start/talker/../..'):
            # FIXME: borken.xml
            paras = elem.xpath('./talk.text/body/p | ./talk.start/para | ./para | ./talk.text/para')
            elem_ctxt = ctxt.create(elem)
            if elem_ctxt is None:
                continue
            for para in paras:
                lines = [t.strip() for t in xml2text(para).splitlines()]
                yield elem_ctxt, lines

    haiku = [5, 7, 5]
    counter = Syllables()

    db.create_all()
    db.session.commit()

    def make_haiku(xml_file):
        csv_header = [ t.name for t in Haiku.__table__.columns ]
        def get_haiku():
            for ctxt, para in para_iter(xml_file):
                for poem in poem_finder(counter, word_stream(para), haiku):
                    yield ctxt.get('\n'.join(' '.join(line) for line in poem.get()))

        fname = os.path.abspath('tmp/out.csv')
        with open(fname, 'w') as fd:
            w = csv.writer(fd)
            w.writerow(csv_header)
            for idx, doc in enumerate(t.get() for t in get_haiku()):
                w.writerow([str(doc[t]).replace('\n','') for t in csv_header])
        conn = db.session.connection()
        res = conn.execute('COPY %s FROM %%s CSV HEADER' % ('haiku'), (fname, ))
        db.session.commit()
        return idx+1

    files = sys.argv[1:]
    for i, xml_file in enumerate(sys.argv[1:]):
        sys.stderr.write("%d/%d: %s... " % (i+1, len(files), os.path.basename(xml_file)))
        sys.stderr.flush()
        doc_count = make_haiku(xml_file)
        sys.stderr.write("%d\n" % (doc_count))
        sys.stderr.flush()
    print("%d haiku in the Hansard." % (issuer.ngen))
