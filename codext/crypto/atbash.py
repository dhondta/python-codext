# -*- coding: UTF-8 -*-
"""Atbash Cipher Codec - atbash content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://crypto.interactive-maths.com/atbash-cipher.html
"""
from ..__common__ import *


ENCMAP = {
    'a': "Z", 'b': "Y", 'c': "X", 'd': "W", 'e': "V", 'f': "U", 'g': "T", 'h': "S", 'i': "R", 'j': "Q", 'k': "P",
    'l': "O", 'm': "N", 'n': "M", 'o': "L", 'p': "K", 'q': "J", 'r': "I", 's': "H", 't': "G", 'u': "F", 'v': "E",
    'w': "D", 'x': "C", 'y': "B", 'z': "A", ' ': " ",
}


add_map("atbash", ENCMAP, ignore_case="both", pattern=r"atbash(?:[-_]cipher)?$")
