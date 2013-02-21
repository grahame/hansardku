
class Syllables:
    def lookup(self, word):
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

