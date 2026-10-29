# -*- coding: UTF-8 -*-
"""ARMON-64 Codec - ARMON-64 content encryption.

ARMON-64 is a toy cipher found on online JavaScript encryption tools, a variant of AER-256. The text is split into
 blocks of half the key length (rounded up), each block being read as a big-endian number of its character codes. For
 each character of the key (at least 3), its code is added to, divides, is subtracted from or (multiplied by 0.01)
 multiplies this number in turn (in floating-point arithmetic), and the resulting numbers are written as JavaScript
 would (e.g. "123.456") and separated by "+" (numbers in exponent notation, e.g. "1e+21", being kept whole when
 decrypting, unlike in the original JavaScript). Decryption applies the inverse operations in reverse order and rounds
 the result. As numbers are double-precision floats, blocks of more than 6 characters (i.e. keys of more than 12
 characters) lose precision and generally cannot be fully decrypted. Only characters with a code below 256 can be
 encrypted, and null characters at the start of a block are lost.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://github.com/gungunfebrianza/Mastering-Cryptography/blob/master/ARMON-64/ARMON-64.js
"""
from ._jsfloat import float_cipher
from ..__common__ import add


__examples__ = {
    'enc(armon64|armon64-ab)':        None,
    'enc(armon64-test|armon-64_test)': {'this is a test': "210.18970297029702+177.9738613861386+-36.77544554455446+"
                                                          "206.4225742574257+153.49900990099007+210.15524752475247+"
                                                          "207.38732673267327"},
    'dec(armon64-test)':              {'210.18970297029702+177.9738613861386': "this", '210.1+x': None},
    'enc-dec(armon64-key|armon64-secret|armon64-K3y!|armon64-123456789012)': ["", "this is a test",
                                                                             "Hello, World! 123", "\xe9t\xe9 \xff"],
}


add("armon64", *float_cipher("armon64", "+", 4), r"^armon[-_]?64(?:[-_](\S*))?$", guess=None)
