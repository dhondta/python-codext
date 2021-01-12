# -*- coding: UTF-8 -*-
"""Bacon's Cipher Codec - bacon content encoding.

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


add_map("bacon", ENCMAP, ignore_case="both", pattern=r"bacon(?:(?:ian)?[-_]cipher)?([\-_].{2})?$", printables_rate=1.)

