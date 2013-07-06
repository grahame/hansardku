#!/usr/bin/env python3

from syllables import Syllables
import re, sys
sys.path.append('../numword')
import numword

class Poem:
    def __init__(self, lines):
        self.lines = lines

    def __repr__(self):
        print(self.lines)
        return ' / '.join(' '.join(line) for line in self.lines)

    def get(self):
        return self.lines

    spring = { 'spring', 'haru', 'warm', 'mist', 'haze', 'blossom', 'doll', 'frog', 'skylark', 'lark', 'warbler', 'whale', 'cherry', 'wildflower', 'flower' }
    summer = { 'summer', 'dog', 'midsummer', 'hot', 'hotness', 'sweat', 'conditioning', 'pleiades', 'smog', 'sunset', 'field', 'meadow', 'waterfall', 'nap', 'siesta', 'nudity', 'nude', 'surfing', 'beach', 'volleyball', 'rollerblading', 'skateboarding', 'sushi', 'sunbathing', 'swimming', 'pool', 'cicada', 'cuckoo', 'jellyfish', 'mosquito', 'snakes', 'lily', 'lotus', 'sunflower', 'wisteria' }
    autumn = { 'autumn', 'moon', 'typhoon', 'thunder', 'scarecrow', 'insect', 'insects', 'cricket', 'crickets', 'nashi', 'pear', 'leaves' }
    winter = { 'winter', 'cold', 'snow', 'soup', 'pumpkin', 'hearth', 'rain' }
    categories = { 'spring' : spring, 'summer' : summer, 'autumn' : autumn, 'winter' : winter }
    word_re = re.compile(r'^([a-z]+)')

    def kigo(self):
        for line in self.lines:
            for word in line:
                m = Poem.word_re.match(word)
                if not m: continue
                word = m.groups()[0].lower()
                for category in Poem.categories:
                    if word in Poem.categories[category]:
                        return category

class Possibility:
    def __init__(self, pattern):
        self.pattern = pattern
        self.lines = []
        self.line = []
        self.line_count = 0
        self.alive = True

    def add(self, count, word):
        if not self.alive:
            return
        self.line.append(word)
        self.line_count += count
        target = self.pattern[len(self.lines)]
        if self.line_count == target:
            self.lines.append(self.line)
            self.line = []
            self.line_count = 0
            if len(self.lines) == len(self.pattern):
                self.alive = False
                return Poem(self.lines)
        elif self.line_count > target:
            self.alive = False

    def is_alive(self):
        return self.alive

def poem_finder(counter, stream, pattern):
    possibilities = []
    for word in stream:
        count = counter.lookup(word)
        possibilities.append(Possibility(pattern))
        for possibility in possibilities:
            poem = possibility.add(count, word)
            if poem:
                yield poem
        possibilites = [t for t in possibilities if t.is_alive()]

number_re = re.compile(r'^\d+$')
def word_stream(line_iter):
    for line in line_iter:
        for word in (t.strip() for t in line.split()):
            if number_re.match(word):
                if len(word) == 4:
                    words = numword.year(int(word))
                else:
                    words = numword.cardinal(int(word))
                for num_word in words:
                    yield words
            else:
                yield word

if __name__ == '__main__':
    import sys

    haiku = [5, 7, 5]
    counter = Syllables()

    for poem in poem_finder(counter, word_stream((t.strip() for t in sys.stdin)), haiku):
        for line in poem:
            print(' '.join(line))
        print()
