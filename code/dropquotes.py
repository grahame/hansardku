#!/usr/bin/env python3

import re, unittest

apostrophe_re = re.compile(r'(\s|^)([\'`’ʼʻ‘].*[\'`’ʼʻ‘])(\s|$)')
quotation_mark_re = re.compile(r'(\s|^)(["“”].*["“”])(\s|$)')
def dropquotes(l):
    def chained_search(s):
        for r in (apostrophe_re, quotation_mark_re):
            m = r.search(s)
            if m:
                return m
    r = []
    while True:
        match = chained_search(l)
        if not match:
            break
        inner = l[match.start():match.end()]
        print("drop:", inner)
        r.append(l[:match.start()])
        l = l[match.end():]
    if l:
        r.append(l)
    return r

class TestQuotes(unittest.TestCase):
    def check_known(self, s, r):
        self.assertEqual(dropquotes(s), r)

    def test_simple(self):
        self.check_known("this is a 'fun test of its fun' goat", ["this is a", "goat"])

    def test_it_is(self):
        self.check_known("this is a 'fun test of it's fun' goat", ["this is a", "goat"])

    def test_simple_quotation(self):
        self.check_known("this is a “fun test of its fun” goat", ["this is a", "goat"])

    def test_two_quotes(self):
        self.check_known(
            "known 'asparagus traders' do eat 'their greens' womble's",
            ["known", "do eat", "womble's"])
    

if __name__ == '__main__':
    unittest.main()
