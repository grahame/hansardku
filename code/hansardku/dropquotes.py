#!/usr/bin/env python3

import re, unittest

apostrophe_re = re.compile(r'(\s|^)[\'`’ʼʻ‘]([^\'`’ʼʻ‘]|[\'`’ʼʻ‘]\w)+[\'`’ʼʻ‘](\s|$)')
quotation_mark_re = re.compile(r'(\s|^)["“”][^"“”]+["“”](\s|$)')
def dropquotes(l, test_fn=None):
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
        drop = True
        if test_fn is not None:
            drop = test_fn(inner)
        if drop:
            r.append(l[:match.start()])
        else:
            r.append(l[:match.end()])            
        l = l[match.end():]
    r.append(l)
    return [t for t in r if t]

class TestQuotes(unittest.TestCase):
    def check_known(self, s, r):
        self.assertEqual(dropquotes(s), r)

    def test_simple(self):
        self.check_known("this is a 'fun test of its fun' goat", ["this is a", "goat"])

    def test_it_is(self):
        self.check_known("this is a 'fun test of it's fun' goat", ["this is a", "goat"])

    def test_simple_quotation(self):
        self.check_known("this is a “fun test of its fun” goat", ["this is a", "goat"])

    def test_two_apostrophe(self):
        self.check_known(
            "known 'asparagus traders' do eat 'their greens' womble's",
            ["known", "do eat", "womble's"])
    
    def test_two_apostrophe_no_lead(self):
        self.check_known(
            "'asparagus traders' 'their greens'",
            [])

    def test_two_quotes(self):
        self.check_known(
            "known \"asparagus traders\" do eat \"their greens\" womble's",
            ["known", "do eat", "womble's"])

if __name__ == '__main__':
    unittest.main()
