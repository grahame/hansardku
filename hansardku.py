#!/usr/bin/env python3

from lxml import etree
import sys
from xml2text import xml2text
from haiku import word_stream, poem_finder, Syllables

if __name__ == '__main__':
    #counter = Syllables()
    #poem_finder(word_stream(), haiku, callback)

    def get_speeches(xml_file):
        pass
    
    def one(e, p):
        m = e.xpath(p)
        if not m:
            return
        assert(len(m) == 1)
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

    class HaikuContextFactory:
        def __init__(self, et):
            self.date = one(et, '/session.header/date')

        def create(self, elem):
            return {
                'date' : self.date,
                'name.id' : one(elem, './talk.start/talker/name.id'),
                'name' : one(elem, './talk.start/talker/name'),
                'party' : one(elem, './talk.start/talker/party')
            }

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
            for para in paras:
                lines = [t.strip() for t in xml2text(para).splitlines()]
                yield elem_ctxt, lines

    def callback(ctxt, poem):
        print("Context:", ctxt)
        for line in poem:
            print(' '.join(line))
        print()

    haiku = [5, 7, 5]
    counter = Syllables()

    def make_haiku(xml_file):
        for ctxt, para in para_iter(xml_file):
            print(ctxt, para)
            poem_finder(counter, word_stream(para), haiku, lambda c: callback(ctxt, c))

    for xml_file in sys.argv[1:]:
        make_haiku(xml_file)


