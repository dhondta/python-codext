# -*- coding: UTF-8 -*-
"""Bacon's Cipher Codec - bacon content encoding.

Bacon's cipher was devised by Francis Bacon in 1605 as a steganographic method: each letter is written as a group of 5
 symbols among two ("a" and "b"), which can then be hidden e.g. in the choice between two typefaces. This implementation
 uses the original 24-letter alphabet, in which I and J, as well as U and V, share the same code. The two symbols can be
 chosen in the codec name (e.g. "bacon-01" or "bacon-ba").

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Bacon%27s_cipher
"""
from ..__common__ import *


__examples__ = {
    'enc(bacon|bacon_cipher|baconian-cipher|bacon-ab|bacon_AB)': {
        'this is a test': "baabaaabbbabaaabaaab abaaabaaab aaaaa baabaaabaabaaabbaaba",
    },
    'enc(bacon-01|bacon_01)': {
        'this is a test': "10010001110100010001 0100010001 00000 10010001001000110010",
    },
}
__guess__ = {"bacon", "bacon-ba", "bacon-01", "bacon-10"}


ENCMAP = {
    'A': "aaaaa", 'B': "aaaab", 'C': "aaaba", 'D': "aaabb", 'E': "aabaa", 'F': "aabab", 'G': "aabba", 'H': "aabbb",
    'I': "abaaa", 'J': "abaaa", 'K': "abaab", 'L': "ababa", 'M': "ababb", 'N': "abbaa", 'O': "abbab", 'P': "abbba",
    'Q': "abbbb", 'R': "baaaa", 'S': "baaab", 'T': "baaba", 'U': "baabb", 'V': "baabb", 'W': "babaa", 'X': "babab",
    'Y': "babba", 'Z': "babbb", ' ': " ",
}


add_map("bacon", ENCMAP, ignore_case="both", pattern=r"bacon(?:(?:ian)?[-_]cipher)?([\-_].{2})?$", expansion_factor=5.,
        printables_rate=1.)

