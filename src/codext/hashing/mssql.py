# -*- coding: UTF-8 -*-
"""MSSQL Hashing Codecs - string hashing with the Microsoft SQL Server password hashes.

Microsoft SQL Server stores a password as "0x0100" followed by a 4-byte random salt and the SHA-1 digest of the
 password (encoded in UTF-16LE) concatenated with the salt, in hexadecimal. The 2000 version appends a second digest,
 of the uppercased password, for case-insensitive verification ; the 2005 version drops it. A random salt is generated
 each time, hence the output differs between calls. These codecs return the hash string (one-way), for use with other
 codecs in encoding chains.

These codecs:
- transform strings from str to str
- transform strings from bytes to bytes
- transform file content from str to bytes (write)

Reference: https://passlib.readthedocs.io/en/stable/lib/passlib.hash.mssql2000.html
"""
import os

from ..__common__ import *


def _sha1(text, salt):
    return hashlib.sha1(ensure_str(text).encode("utf-16-le") + salt).digest()


def mssql_hash(old):
    def _hash(text, errors="strict"):
        t, salt = ensure_str(text), os.urandom(4)
        digest = _sha1(t, salt) + (_sha1(t.upper(), salt) if old else b"")
        return "0x0100" + (salt + digest).hex().upper(), len(text)
    return _hash


add("mssql2000", mssql_hash(True), pattern=r"^mssql[-_]?2000$", guess=None)
add("mssql2005", mssql_hash(False), pattern=r"^mssql[-_]?2005$", guess=None)
