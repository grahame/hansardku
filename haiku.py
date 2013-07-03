#!/usr/bin/env python3

from syllables import Syllables
import re, sys
sys.path.append('./numword')
import numword

def poem_finder(counter, stream, pattern, callback):
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
                    callback(self.lines)
                    return False
            elif self.line_count > target:
                return False
            return True

    possibilities = []
    for word in stream:
        count = counter.lookup(word)
        possibilities.append(Possibility())
        possibilities = list(filter(lambda p: p.add(count, word), possibilities))

number_re = re.compile(r'^\d+$')
def word_stream(line_iter):
    for line in line_iter:
        for word in (t.strip() for t in line.split()):
            if number_re.match(word):
                for num_word in word_to_num(len(word), int(word)):
                    yield num_word
            else:
                yield word

if __name__ == '__main__':
    import sys

    def callback(poem):
        for line in poem:
            print(' '.join(line))
        print()

    haiku = [5, 7, 5]
    counter = Syllables()
    poem_finder(counter, word_stream((t.strip() for t in sys.stdin)), haiku, callback)

