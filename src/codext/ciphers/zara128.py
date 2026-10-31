# -*- coding: UTF-8 -*-
"""ZARA-128 Codec - ZARA-128 content encryption.

ZARA-128 is a toy cipher found on online JavaScript encryption tools, a variant of AER-256 with a single operation. The
 text is split into blocks of a fifth of the key length (rounded), each block being read as a big-endian number of its
 character codes. The code of each character of the key (at least 3) is added to this number, and the resulting numbers
 are separated by " ". Decryption subtracts the codes of the key. As numbers are double-precision floats, blocks of more
 than 6 characters (i.e. keys of more than 32 characters) lose precision and generally cannot be fully decrypted. Only
 characters with a code below 256 can be encrypted, and null characters at the start of a block are lost.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: http://qbarbe.free.fr/crypto/eng_zara128p.php
"""
from ._jsfloat import float_cipher
from ..__common__ import add


__examples__ = {
    'enc(zara128|zara128-ab)':          None,
    'enc(zara128-016359|zara-128_016359)': {'test': "428 413 427 428"},
    'enc(zara128-secretkey)':           {'test': "30772 30531"},
    'dec(zara128-016359)':              {'428 413': "te", '428 x': None},
    'enc-dec(zara128-key|zara128-secret|zara128-K3y!|zara128-12345678901234567890123456789012)':
        ["", "this is a test", "Hello, World! 123", "\xe9t\xe9 \xff"],
}


add("zara128", *float_cipher("zara128", " ", 1, 5), r"^zara[-_]?128(?:[-_](\S*))?$", guess=None)
