#!/usr/bin/env python3

from syllables import Syllables
import re, sys
sys.path.append('./numword')
import numword

def poem_finder(counter, stream, pattern):
    class Possibility:
        def __init__(self):
            self.lines = []
            self.line = []
            self.line_count = 0

        def add(self, count, word):
            self.line.append(word)
            self.line_count += count
            target = pattern[len(self.lines)]
            if self.line_count == target:
                self.lines.append(self.line)
                self.line = []
                self.line_count = 0
                if len(self.lines) == len(pattern):
                    return False, self.lines
            elif self.line_count > target:
                return False, None
            return True, None

    possibilities = []
    for word in stream:
        count = counter.lookup(word)
        possibilities.append(Possibility())
        next_possibilities = []
        for possibility in possibilities:
            cont, lines = possibility.add(count, word)
            if lines:
                yield lines
            if cont:
                next_possibilities.append(possibility)
        possibilities = next_possibilities

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
