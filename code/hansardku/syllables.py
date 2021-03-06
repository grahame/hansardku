import re, string, sys, os, json
from roman import decode_roman
from lxml import etree
sys.path.append('../numword')
import numword

def read_gcide_syllables():
    gcide_filename = 'tmp/gcide.json'
    if os.access(gcide_filename, os.R_OK):
        with open(gcide_filename, 'r') as fd:
            return json.load(fd)

    word_splitter = re.compile(r' |\t|-')
    accent_splitter = re.compile(r'[\*|\-|\"|\`]+')
    res = {}
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

    with open(gcide_filename, 'w') as fd:
        json.dump(res, fd)
    return res


number_re = re.compile(r'^\d+(\.\d+)?$')

class Syllables:
    check_suffixes = (None, 'esque', 'able', 'ible', 'ance',
        'ical', 'ious', 'ence', 'ment', 'ness', 'ship', 'less', 'sion',
        'tion', 'ical', 'ous', 'ful', 'ate', 'ify', 'ive', 'ing', 'ize',
        'ise', 'ism', 'ic', 'ist', 'er', 'fy', 'or', 'en', 'y')
    # credit: http://stackoverflow.com/questions/267399/how-do-you-match-only-valid-roman-numerals-with-a-regular-expression
    roman_re = re.compile(r'^(ix|iv|v?i{0,3})$')

    def __init__(self):
        self.known = {}
        self.hit = self.miss = 0
        self.known = read_gcide_syllables()

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

    def _lookup(self, word):
        lower_word = word.lower()
        # roman numerals
        if len(lower_word) > 1 and Syllables.roman_re.match(lower_word):
            words = numword.cardinal(decode_roman(lower_word)).split()
            return sum(self.lookup(word) for word in words)
        # numbers
        if number_re.match(word):
            iword = int(word)
            if len(word) == 4:
                fn = numword.year
            else:
                fn = numword.cardinal
            words = fn(iword).split()
            return sum(self.lookup(word) for word in words)
        # acronyms – which don't contain numbers
        n_numbers = len([t for t in word if t in string.digits])
        if n_numbers == 0 and len(word) > 1 and len(word) < 5 and (word.upper() == word):
            return len(word)
        # world lookup
        for suffix in Syllables.check_suffixes:
            l = self.check_known(lower_word, suffix)
            if l is not None:
                return l
        # fallback if we can't find the word
        return self.__syllable_estimate(lower_word)

    def lookup(self, *args, **kwargs):
        r = self._lookup(*args, **kwargs)
        # print(args, kwargs, r)
        return r

    def __syllable_estimate(self, token):
        "Last resort syllable counter. Reasonably accurate in English."
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

if __name__ == "__main__":
    counter = Syllables()
    for i in sys.argv[1:]:
        print (i, counter.lookup(i))
