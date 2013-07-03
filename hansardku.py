#!/usr/bin/env python3

from lxml import etree
import sys, os
from xml2text import xml2text
sys.path.append('./couchdb-python3')
import couchdb, itertools
from haiku import word_stream, poem_finder, Syllables

if __name__ == '__main__':
    def take(n, iterable):
        "Return first n items of the iterable as a list"
        return list(itertools.islice(iterable, n))

    def one(e, p):
        m = e.xpath(p)
        if not m:
            return
        elif len(m) > 1:
            print(e, p)
            print(m)
            raise Exception("More than one match!")
        return m[0].text

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
            s = []
            v = self.ngen
            while True:
                i = v % HaikuContextFactory.tbl_len
                v -= i
                v //= HaikuContextFactory.tbl_len
                s.append(HaikuContextFactory.tbl[i])
                if v == 0:
                    break
            r = ''.join(reversed(s))
            self.ngen += 1
            return r

    issuer = TokenIssuer()

    class HaikuContext:
        def __init__(self, doc):
            self.doc = doc

        def get(self, poem):
            return couchdb.Document(_id=issuer.issue(), poem=poem, **self.doc)

    class HaikuContextFactory:
        tbl = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        tbl_len = len(tbl)

        def __init__(self, et):
            self.date = one(et, '/hansard/session.header/date')

        def create(self, elem):
            name = one(elem, './talk.start/talker/name[@role="metadata"]')
            if name is None:
                name = one(elem, './talk.start/talker/name')
            if name.upper().find("PRESIDENT") != -1 or name.upper().find("SPEAKER") != -1:
                return None
            return HaikuContext({
                'date' : self.date,
                'name.id' : one(elem, './talk.start/talker/name.id'),
                'name' : name,
                'party' : one(elem, './talk.start/talker/party')
            })

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
            paras = elem.xpath('.//para|.//p')
            elem_ctxt = ctxt.create(elem)
            if elem_ctxt is None:
                continue
            for para in paras:
                lines = [t.strip() for t in xml2text(para).splitlines()]
                yield elem_ctxt, lines

    srv = couchdb.Server()
    db = srv['hansardku']

    haiku = [5, 7, 5]
    counter = Syllables()

    def make_haiku(xml_file):
        def get_haiku():
            for ctxt, para in para_iter(xml_file):
                for poem in poem_finder(counter, word_stream(para), haiku):
                    yield ctxt.get('\n'.join(' '.join(line) for line in poem))

        it = get_haiku()
        ndocs = 0
        while True:
            docs = take(8192, it)
            if len(docs) == 0:
                break
            db.update(docs)
            ndocs += len(docs)
        return ndocs

    files = sys.argv[1:]
    for i, xml_file in enumerate(sys.argv[1:]):
        sys.stderr.write("%d/%d: %s... " % (i+1, len(files), os.path.basename(xml_file)))
        sys.stderr.flush()
        n = make_haiku(xml_file)
        sys.stderr.write("%d\n" % n)
        sys.stderr.flush()
    print("%d poems in the hansard." % (issuer.ngen))

