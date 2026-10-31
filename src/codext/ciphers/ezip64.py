# -*- coding: UTF-8 -*-
"""EZIP-64 Codec - EZIP-64 content encryption.

EZIP-64 is a toy cipher found on online JavaScript encryption tools, a variant of ARMON-64. The text is split into
 blocks of a third of the key length (rounded), each block being read as a big-endian number of its character codes.
 For each character of the key (at least 3), its code is added to, divides, is subtracted from or (multiplied by 0.02)
 multiplies this number in turn (in floating-point arithmetic), and the resulting numbers are written as JavaScript
 would (e.g. "123.456") and separated by "/". Decryption applies the inverse operations in reverse order and rounds the
 result. As numbers are double-precision floats, blocks of more than 6 characters (i.e. keys of more than 19
 characters) lose precision and generally cannot be fully decrypted. Only characters with a code below 256 can be
 encrypted, and null characters at the start of a block are lost.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: http://qbarbe.free.fr/crypto/eng_ezip64p.php
"""
from ._jsfloat import float_cipher
from ..__common__ import add


__examples__ = {
    'enc(ezip64|ezip64-ab)':        None,
    'enc(ezip64-test|ezip-64_test)': {'test': "-261.47089108910893/-261.81544554455445/-261.4938613861386/"
                                              "-261.47089108910893"},
    'dec(ezip64-test)':              {'-261.47089108910893/-261.81544554455445': "te", '-261.4/x': None},
    'enc-dec(ezip64-key|ezip64-secret|ezip64-K3y!|ezip64-1234567890123456789)': ["", "this is a test",
                                                                                "Hello, World! 123", "\xe9t\xe9 \xff"],
}


add("ezip64", *float_cipher("ezip64", "/", 4, 3, .02), r"^ezip[-_]?64(?:[-_](\S*))?$", guess=None)
