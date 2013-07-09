import re, string, sys
from lxml import etree
sys.path.append('../numword')
import numword

def read_gcide_syllables(res):
    word_splitter = re.compile(r' |\t|-')
    accent_splitter = re.compile(r'[\*|\-|\"|\`]+')
    with open('../xml_files/gcide.xml', 'r') as fd:
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

number_re = re.compile(r'^\d+$')

class Syllables:
    check_suffixes = (None, 'esque', 'able', 'ible', 'ance',
        'ical', 'ious', 'ence', 'ment', 'ness', 'ship', 'less', 'sion',
        'tion', 'ical', 'ous', 'ful', 'ate', 'ify', 'ive', 'ing', 'ize',
        'ise', 'ism', 'ic', 'ist', 'er', 'fy', 'or', 'en', 'y')

    def __init__(self):
        self.known = {}
        self.hit = self.miss = 0
        sys.stderr.write("reading GCIDE...")
        sys.stderr.flush()
        read_gcide_syllables(self.known)
        sys.stderr.write(" done\n")
        sys.stderr.flush()

    def check_known(self, word, suffix):
        if suffix is not None and not word.endswith(suffix):
            return
        if suffix is not None:
            word = word[:-len(suffix)]
        if word not in self.known:
            return
        r = self.known[word]
        if suffix is not None:
            r += self.__syllable_estimate(suffix)
        return r

    def lookup(self, word):
        for suffix in Syllables.check_suffixes:
            l = self.check_known(word, suffix)
            if l is not None:
                return l

        if number_re.match(word):
            iword = int(word)
            if len(word) == 4:
                words = numword.year(iword)
            else:
                words = numword.cardinal(iword)
            return sum(self.lookup(word) for word in words)

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

