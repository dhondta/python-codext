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


ENCMAP = {
    'A': "aaaaa", 'B': "aaaab", 'C': "aaaba", 'D': "aaabb", 'E': "aabaa", 'F': "aabab", 'G': "aabba", 'H': "aabbb",
    'I': "abaaa", 'J': "abaaa", 'K': "abaab", 'L': "ababa", 'M': "ababb", 'N': "abbaa", 'O': "abbab", 'P': "abbba",
    'Q': "abbbb", 'R': "baaaa", 'S': "baaab", 'T': "baaba", 'U': "baabb", 'V': "baabb", 'W': "babaa", 'X': "babab",
    'Y': "babba", 'Z': "babbb", ' ': "",
}


add_map("bacon", ENCMAP, sep=" ", ignore_case="encode", pattern=r"bacon(?:(?:ian)?[-_]cipher)?([\-_].{2})?$")
