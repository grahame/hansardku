
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

    def test_complex(self):
        self.check_result("""<a><b><c><d>First</d></c>Last</b></a>""", "FirstLast")

def xml2text(et):
    return (''.join([(t.text or '') + (t.tail or '') for t in et.xpath('. | .//*')])).strip()

if __name__ == '__main__':
    unittest.main()
