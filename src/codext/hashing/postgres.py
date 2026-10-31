# -*- coding: UTF-8 -*-
"""PostgreSQL Hashing Codec - string hashing with the PostgreSQL MD5 password hash.

PostgreSQL stores a password as "md5" followed by the hexadecimal MD5 digest of the password concatenated with the user
 name. The user name (required, as it is the salt) is given with the codec name (e.g. "postgres-md5-admin"). This codec
 returns the hash string (one-way), for use with other codecs in encoding chains.

This codec:
- transforms strings from str to str
- transforms strings from bytes to bytes
- transforms file content from str to bytes (write)

Reference: https://www.postgresql.org/docs/current/auth-password.html
"""
from ..__common__ import *


def postgres_md5(user=None):
    u = str(user).encode() if user not in (None, "") else b""
    def _hash(text, errors="strict"):
        return "md5" + hashlib.md5(b(text) + u).hexdigest(), len(text)
    return _hash


add("postgres-md5", postgres_md5, pattern=r"^postgres(?:ql)?[-_]md5(?:[-_](.+))?$", guess=None)
