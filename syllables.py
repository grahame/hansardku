import re, string
from lxml import etree

def read_gcide_syllables(res):
    word_splitter = re.compile(r' |\t|-')
    accent_splitter = re.compile(r'[\*|\-|\"|\`]+')
    with open('xml_files/gcide.xml', 'r') as fd:
        doc = etree.parse(fd)
        for definition in (t.text.lower() for t in doc.xpath('//hw') if t.text is not None):
            for word in word_splitter.split(definition):
                word = ''.join(t for t in word if t in string.printable)
                syllables = list(filter(None, accent_splitter.split(word)))
                # if we don't have syllable markup, or result is just silly, give up
                if len(syllables) < 2:
                    continue
                res[''.join(syllables)] = len(syllables)
        del doc

class Syllables:
    def __init__(self):
        self.known = {}
        self.hit = self.miss = 0
        # read_gcide_syllables(self.known)

    def lookup(self, word):
        word = ''.join((t for t in word.lower() if t in string.ascii_letters))
        if word in self.known:
            return self.known[word]
        return self.__syllable_estimate(word)

    def __syllable_estimate(self, token):
        "Last resort syllable counter. Reasonably accurate in English." \
        "Allegedly works for French."
        vowels = ['a', 'e', 'i', 'o', 'u', 'y', "'"]
        l = None
        count = 0
        if len(token) == 0:
            return 0
        if len(token) <= 3:
            return 1
        for c in token:
            if c in vowels and l not in vowels:
                count = count + 1
            l = c
        if count > 1 and ((token[-1] == 'e' and token[-2] != 'l') or 
                          (token[-2] == 'e' and token[-1] == 's')):
            # silent 'e'
            count = count - 1
        if count == 0: count = 1
        return count

