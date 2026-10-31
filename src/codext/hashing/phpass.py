# -*- coding: UTF-8 -*-
"""PHPass Hashing Codec - string hashing with the portable PHP password hash.

PHPass is the portable password hash of the PHP framework (used e.g. by WordPress and phpBB), of the form
 "$P$" (or "$H$"), a character giving the iteration count as a power of 2, an 8-character salt and the hash. The hash
 is the MD5 digest of the salt and password, re-hashed with the password the given number of times, written with the
 "./0-9A-Za-z" alphabet. A random salt is generated each time, hence the output differs between calls ; the iteration
 count is given with the codec name (e.g. "phpass-13", from 7 to 30, defaulting to 13). This codec returns the hash
 string (one-way), for use with other codecs in encoding chains.

This codec:
- transforms strings from str to str
- transforms strings from bytes to bytes
- transforms file content from str to bytes (write)

Reference: https://www.openwall.com/phpass/
"""
import os

from ._h64 import ALPHABET, encode_bytes
from ..__common__ import *


def phpass(rounds=None):
    rounds = int(rounds or 13)
    if not 7 <= rounds <= 30:
        raise LookupError("Bad parameter for encoding 'phpass': iteration count must be between 7 and 30")
    def _hash(text, errors="strict"):
        data = b(ensure_str(text))
        salt = "".join(ALPHABET[c & 63] for c in os.urandom(8))
        digest = hashlib.md5(salt.encode() + data).digest()
        for _ in range(1 << rounds):
            digest = hashlib.md5(digest + data).digest()
        return "$P$" + ALPHABET[rounds] + salt + encode_bytes(digest), len(text)
    return _hash


add("phpass", phpass, pattern=r"^phpass(?:[-_](\d{1,2}))?$", guess=None)
