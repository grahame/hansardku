#!/usr/bin/env python3

from syllables import Syllables

def poem_finder(stream, pattern):
    counter = Syllables()

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
                    print(self.lines)
                    return False
            elif self.line_count > target:
                return False
            return True

    possibilities = []
    for word in stream:
        count = counter.lookup(word)
        print(word, count)
        possibilities.append(Possibility())
        possibilities = list(filter(lambda p: p.add(count, word), possibilities))

if __name__ == '__main__':
    import sys
    def word_stream():
        for word in (t.strip() for t in sys.stdin.readlines()):
            yield word

    haiku = [5, 7, 5]
    poem_finder(word_stream(), haiku)

