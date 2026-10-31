# -*- coding: UTF-8 -*-
"""OKTO3 Codec - OKTO3 content encryption.

OKTO3 is a toy cipher found on online JavaScript encryption tools, a variant of AER-256. The text is split into blocks
 of a sixth of the key length (rounded), each block being read as a big-endian number of its character codes. For each
 character of the key (at least 3), its code is added to, divides, is subtracted from or (multiplied by 500.005)
 multiplies this number in turn (in floating-point arithmetic), and the resulting numbers are written as JavaScript
 would (e.g. "123.456") and separated by a newline. Decryption applies the inverse operations in reverse order and
 rounds the result. As numbers are double-precision floats, blocks of more than 6 characters (i.e. keys of more than 36
 characters) lose precision and generally cannot be fully decrypted. Only characters with a code below 256 can be
 encrypted, and null characters at the start of a block are lost.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: http://qbarbe.free.fr/crypto/eng_okto3p.php
"""
from ._jsfloat import float_cipher
from ..__common__ import add


__examples__ = {
    'enc(okto3|okto3-ab)':        None,
    'enc(okto3-test|okto-3_test)': {'test': "-6536837.644950495\n-6545451.592475248\n-6537411.908118811\n"
                                            "-6536837.644950495"},
    'dec(okto3-test)':            {'-6536837.644950495\n-6545451.592475248': "te", '-6536837.6\nx': None},
    'enc-dec(okto3-key|okto3-secret|okto3-K3y!|okto3-123456789012)': ["", "this is a test", "Hello, World! 123",
                                                                     "\xe9t\xe9 \xff"],
}


add("okto3", *float_cipher("okto3", "\n", 4, 6, 500.005), r"^okto[-_]?3(?:[-_](\S*))?$", guess=None)
