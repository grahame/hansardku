
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

    def test_two_element_lead(self):
        self.check_result("<a>angry<b>goat</b></a>", "angrygoat")

    def test_two_element_tail(self):
        self.check_result("<a><b>power</b>goat</a>", "powergoat")

    def test_three_element_all(self):
        self.check_result("""<a>1<b>2<c>3</c>4</b>5</a>""", "12345")

    def test_three_element_nested_tail(self):
        self.check_result("""<a><b><c>First</c></b>Last</a>""", "FirstLast")

    def test_three_element_nested_lead(self):
        self.check_result("""<a>First<b><c>Last</c></b></a>""", "FirstLast")

    def test_four_element_all(self):
        self.check_result("""<a>1<b>2<c>3<d>4</d>5</c>6</b>7</a>""", "1234567")

def xml2text(et):
    def _rec(elem):
        return (elem.text or '') + ''.join( _rec(child) for child in elem.xpath('./*') ) + (elem.tail or '')
    # cope if we've been given an elementtree rather than an element
    return _rec(et.xpath('.')[0])

if __name__ == '__main__':
    unittest.main()
