#!/usr/bin/env python3

from lxml import etree
import sys
from xml2text import xml2text

if __name__ == '__main__':
    #counter = Syllables()
    #poem_finder(word_stream(), haiku, callback)

    def get_speeches(xml_file):
        pass
    
    def make_haiku(xml_file):
        with open(xml_file, 'rb') as fd:
            e = etree.parse(fd)
        elems = e.xpath('//talk.start/talker/../..')
        for elem in elems:
            print("****************************")
            paras = elem.xpath('.//para|.//body')
            lines = []
            for para in paras:
                lines += (t.strip() for t in xml2text(para).splitlines())
            for line in lines:
                print(line)
    
    for xml_file in sys.argv[1:]:
        make_haiku(xml_file)


