import unittest

chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
base = 62
assert(len(chars) == base)

def encode(v):
    s = []
    while True:
        i = v % base
        v //= base
        s.append(chars[i])
        if v == 0:
            break
    return ''.join(reversed(s))

def decode(v):
    r = 0
    for c in reversed(v):
        r *= base
        r += chars.index(c)
    return r

class TestBase62(unittest.TestCase):
    def known(self, f, t):
        self.assertEqual(decode(t), f)
        self.assertEqual(encode(f), t)        

    def test_0(self):
        self.known(0, 'a')

    def test_1(self):
        self.known(1, 'b')

    def test_chars(self):
        for n in range(1,5):
            for c in chars:
                t = n*c
                print(t, decode(t), encode(decode(t)))
                self.assertEqual(encode(decode(t)), t)

    def test_base(self):
        for v in range(base):
            self.assertEqual(decode(encode(v)), v)


if __name__ == '__main__':
    unittest.main()
