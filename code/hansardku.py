#!/usr/bin/env python3

from lxml import etree
import sys, os
from xml2text import xml2text
import itertools
from haiku import word_stream, poem_finder, Syllables

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
            v = int_id = self.ngen
            self.ngen += 1
            return int_id

    issuer = TokenIssuer()

    class HaikuWrapper:
        def __init__(self, kwargs):
            self.doc = kwargs

    class HaikuContext:
        def __init__(self, doc):
            self.doc = doc

        def get(self, poem, kigo):
            return HaikuWrapper(id=issuer.issue(), poem=poem, kigo=kigo, **self.doc)

    class HaikuContextFactory:
        tbl = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        tbl_len = len(tbl)

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
                'name.id' : oneof(elem, './talk.start/talker/name.id'),
                'name' : name,
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

    def make_haiku(xml_file):
        def get_haiku():
            for ctxt, para in para_iter(xml_file):
                for poem in poem_finder(counter, word_stream(para), haiku):
                    yield ctxt.get('\n'.join(' '.join(line) for line in poem.get()), poem.kigo())

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
    print("%d haiku in the Hansard." % (issuer.ngen))
