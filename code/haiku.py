#!/usr/bin/env python3

from syllables import Syllables
import re, sys, string
import unittest

class Poem:
    def __init__(self, lines):
        self.lines = lines

    def __repr__(self):
        print(self.lines)
        return ' / '.join(' '.join(line) for line in self.lines)

    def get(self):
        return self.lines

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

split_re = re.compile(r'\W+')
def to_alphanum(word):
    return ''.join((t for t in word.lower() if t in string.ascii_letters or t in string.digits))

def token_subwords(token):
    return [to_alphanum(subword) for subword in split_re.split(token)]

def token_syllable_count(counter, token):
    subwords = token_subwords(token)
    return sum(counter.lookup(subword) for subword in subwords if subword)

def poem_finder(counter, stream, pattern):
    possibilities = []
    for token in stream:
        count = token_syllable_count(counter, token)
        possibilities.append(Possibility(pattern))
        for possibility in possibilities:
            poem = possibility.add(count, token)
            if poem:
                yield poem
        possibilites = [t for t in possibilities if t.is_alive()]

def token_stream(line_iter):
    for line in line_iter:
        for word in (t.strip() for t in line.split()):
            yield word

class TokenCountTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TokenCountTest, self).__init__(*args, **kwargs)
        self.counter = Syllables()

    def check_count(self, tok, c):
        try:
            self.assertEqual(token_syllable_count(self.counter, tok), c)
        except:
            print("Failure: %s -> %d (should have been %d)" % (repr(tok), token_syllable_count(self.counter, tok), c))
            raise

    def test_simple(self):
        self.check_count("the", 1)

    def check_number(self, mutator=None):
        counts = {
            "0": 2,
            "1": 1,
            "2": 1,
            "3": 1,
            "4": 1,
            "5": 1,
            "6": 1,
            "7": 2,
            "8": 1,
            "9": 1,
            "10": 1,
            "11": 3,
            "110": 5,
            "1000": 3,
            }
        for i, v in sorted(counts.items()):
            if mutator is not None:
                i = mutator(i)
            self.check_count(i, v)

    def test_number(self):
        self.check_number()

    def test_dollars(self):
        self.check_number(lambda n: '$'+n)

    def test_leading_punctuation(self):
        self.check_count("the", 1)

    def test_hyphenated(self):
        for hyphen in ['-', '–']:
            self.check_count(hyphen.join(['one', 'thousand']), 3)

if __name__ == '__main__':
    unittest.main()
