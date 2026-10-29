# -*- coding: UTF-8 -*-
"""MySQL Hashing Codecs - string hashing with the MySQL password hashes.

MySQL 3.23 hashed passwords with a custom 64-bit function (ignoring spaces and tabs), written as 16 hexadecimal digits,
 while MySQL 4.1 introduced the "mysql_native_password" hash, i.e. "*" followed by the uppercase hexadecimal SHA-1
 digest of the binary SHA-1 digest of the password. These codecs return the hash in these formats (one-way), for use
 with other codecs in encoding chains.

These codecs:
- transform strings from str to str
- transform strings from bytes to bytes
- transform file content from str to bytes (write)

Reference: https://dev.mysql.com/doc/refman/8.4/en/password-hashing.html
"""
from ..__common__ import *


def mysql323(text, errors="strict"):
    nr, nr2, inc, m = 1345345333, 0x12345671, 7, 0xffffffff
    for c in b(text):
        if c in b" \t":
            continue
        nr ^= (((nr & 63) + inc) * c + (nr << 8)) & m
        nr2 = (nr2 + ((nr2 << 8) ^ nr)) & m
        inc = (inc + c) & m
    return "%08x%08x" % (nr & 0x7fffffff, nr2 & 0x7fffffff), len(text)


def mysql41(text, errors="strict"):
    return "*" + hashlib.sha1(hashlib.sha1(b(text)).digest()).hexdigest().upper(), len(text)


add("mysql323", mysql323, pattern=r"^mysql[-_]?3(?:\.?23)?$", guess=None)
add("mysql41", mysql41, pattern=r"^mysql[-_]?4(?:\.?1)?$", guess=None)
