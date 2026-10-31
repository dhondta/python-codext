# -*- coding: UTF-8 -*-
"""AER-256 Codec - AER-256 content encryption.

AER-256 is a toy cipher found on online JavaScript encryption tools. The text is split into blocks of half the key
 length (rounded up), each block being read as a big-endian number of its character codes. For each character of the key
 (at least 3), its code is added to, divides or is subtracted from this number in turn (in floating-point arithmetic),
 and the resulting numbers are written as JavaScript would (e.g. "123.456") and separated by ", ". Decryption applies
 the inverse operations in reverse order and rounds the result. As numbers are double-precision floats, blocks of more
 than 6 characters (i.e. keys of more than 12 characters) lose precision and generally cannot be fully decrypted. Only
 characters with a code below 256 can be encrypted, and null characters at the start of a block are lost.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://github.com/gungunfebrianza/Mastering-Cryptography/blob/master/AER-256/AER-256.js
"""
from ._jsfloat import float_cipher
from ..__common__ import add


__examples__ = {
    'enc(aer256|aer256-ab)':      None,
    'enc(aer256-key|aer-256_key)': {'this is a test': "175.10891089108912, 147.33663366336634, -37.79207920792079, "
                                                      "171.86138613861385, 126.23762376237624, 175.0792079207921, "
                                                      "172.69306930693068"},
    'dec(aer256-key)':            {'175.10891089108912, 147.33663366336634': "this", '175.1, x': None},
    'enc-dec(aer256-key|aer256-secret|aer256-K3y!|aer256-123456789012)': ["", "this is a test", "Hello, World! 123",
                                                                         "\xe9t\xe9 \xff"],
}


add("aer256", *float_cipher("aer256", ", ", 3), r"^aer[-_]?256(?:[-_](\S*))?$", guess=None)
