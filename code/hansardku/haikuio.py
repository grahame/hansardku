
from syllables import Syllables
from haiku import poem_finder, token_stream

if __name__ == '__main__':
    import sys

    haiku = [5, 7, 5]
    counter = Syllables()

    for poem in poem_finder(counter, token_stream((t.strip() for t in sys.stdin)), haiku):
        for line in poem:
            print(' '.join(line))
        print()
