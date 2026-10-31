# -*- coding: UTF-8 -*-
"""Oracle Hashing Codecs - string hashing with the Oracle database password hashes.

The legacy Oracle 10g hash encrypts the uppercased user name and password (encoded in UTF-16BE) with DES in CBC mode,
 twice (the last block of the first pass being the key of the second), the hash being the last block ; the user name
 (the salt) is given with the codec name (e.g. "oracle10-SYSTEM"). The Oracle 11g hash ("S:") is the SHA-1 digest of
 the password followed by a 10-byte random salt, hence its output differs between calls. These codecs return the hash
 string (one-way), for use with other codecs in encoding chains.

These codecs:
- transform strings from str to str
- transform strings from bytes to bytes
- transform file content from str to bytes (write)

Reference: https://www.sans.org/blog/exploiting-the-oracle-login-protocol/
"""
import os

from .windows import des_encrypt
from ..__common__ import *


ORACLE10_MAGIC = b"\x01\x23\x45\x67\x89\xAB\xCD\xEF"


def _des_cbc(key, value):
    """ DES-CBC encryption of the null-padded value with a zero IV, returning only the last block. """
    value += b"\x00" * (-len(value) % 8)
    block = b"\x00" * 8
    for i in range(0, len(value), 8):
        block = des_encrypt(key, bytes(a ^ b for a, b in zip(block, value[i:i+8])))
    return block


def oracle10(user=None):
    u = str(user) if user not in (None, "") else ""
    def _hash(text, errors="strict"):
        data = (u + ensure_str(text)).upper().encode("utf-16-be")
        return _des_cbc(_des_cbc(ORACLE10_MAGIC, data), data).hex().upper(), len(text)
    return _hash


def oracle11(text, errors="strict"):
    salt = os.urandom(10)
    return "S:" + (hashlib.sha1(b(text) + salt).hexdigest() + salt.hex()).upper(), len(text)


add("oracle10", oracle10, pattern=r"^oracle[-_]?10g?(?:[-_](.+))?$", guess=None)
add("oracle11", oracle11, pattern=r"^oracle[-_]?11g?$", guess=None)
