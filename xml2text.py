
import unittest

class TextXml2Text(unittest.TestCase):
    def check_result(self, xmldoc, b):
        from lxml import etree
        from io import StringIO
        et = etree.parse(StringIO(xmldoc))
        self.assertEqual(xml2text(et), b)

    def test_one_element_empty(self):
        self.check_result("<a></a>", "")

    def test_one_element_body(self):
        self.check_result("<a>goat</a>", "goat")

    def test_element_lead(self):
        self.check_result("<a>angry<b>goat</b></a>", "angrygoat")

    def test_element_tail(self):
        self.check_result("<a><b>power</b>goat</a>", "powergoat")

    def test_two_element_all(self):
        self.check_result("""<a>First<b>Second<c>Third</c>Fourth</b>Fifth</a>""", "FirstSecondThirdFourthFifth")

    def test_two_element_nested_tail(self):
        self.check_result("""<a><b><c>First</c></b>Last</a>""", "FirstLast")

    def test_two_element_nested_lead(self):
        self.check_result("""<a>First<b><c>Last</c></b></a>""", "FirstLast")


def xml2text(et):
    def _rec(elem):
        return (elem.text or '') + ''.join( _rec(child) for child in elem.xpath('./*') ) + (elem.tail or '')
    # cope if we've been given an elementtree rather than an element
    return _rec(et.xpath('.')[0])

if __name__ == '__main__':
    unittest.main()
