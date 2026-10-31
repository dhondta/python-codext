# -*- coding: UTF-8 -*-
"""MS-CASH Hashing Codecs - string hashing with the Windows domain cached credentials.

Windows caches domain credentials as MS-CASH (aka Domain Cached Credentials, DCC): MS-CASHv1 (msdcc) is the MD4 digest
 of the NT hash of the password concatenated with the lowercased user name (encoded in UTF-16LE), while MS-CASHv2
 (msdcc2) derives a key from that digest with PBKDF2-HMAC-SHA1 (10240 iterations, the user name as salt). The user name
 (required, as it is the salt) is given with the codec name (e.g. "mscash-Administrator"). These codecs return the
 hexadecimal digest (one-way), for use with other codecs in encoding chains.

These codecs:
- transform strings from str to str
- transform strings from bytes to bytes
- transform file content from str to bytes (write)

Reference: https://openwall.info/wiki/john/MSCash
           https://openwall.info/wiki/john/MSCash2
"""
from .md import md4
from ..__common__ import *


def _dcc(text, user):
    nt = md4(ensure_str(text).encode("utf-16-le"))
    return md4(bytes.fromhex(nt) + user.lower().encode("utf-16-le"))


def mscash(v2):
    def _factory(user=None):
        u = str(user) if user not in (None, "") else ""
        def _hash(text, errors="strict"):
            if not v2:
                return _dcc(text, u), len(text)
            tmp = bytes.fromhex(_dcc(text, u))
            return hashlib.pbkdf2_hmac("sha1", tmp, u.lower().encode("utf-16-le"), 10240, 16).hex(), len(text)
        return _hash
    return _factory


add("mscash", mscash(False), pattern=r"^ms[-_]?cash1?(?:[-_](.+))?$", guess=None)
add("mscash2", mscash(True), pattern=r"^ms[-_]?cash2(?:[-_](.+))?$", guess=None)
