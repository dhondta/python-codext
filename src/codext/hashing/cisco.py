# -*- coding: UTF-8 -*-
"""Cisco PIX/ASA Hashing Codecs - string hashing with the Cisco PIX and ASA password hashes.

The Cisco PIX and ASA firewalls store passwords as the MD5 digest of the password (optionally salted with the user
 name, repeated and padded with null bytes), with every fourth byte of the digest dropped and the result written with
 the "./0-9A-Za-z" alphabet. The user name, when the password is associated with a user account, is given with the
 codec name (e.g. "cisco-asa-admin"). These codecs return the hash string (one-way), for use with other codecs in
 encoding chains.

These codecs:
- transform strings from str to str
- transform strings from bytes to bytes
- transform file content from str to bytes (write)

Reference: https://passlib.readthedocs.io/en/stable/lib/passlib.hash.cisco_asa.html
"""
from ._h64 import encode_bytes
from ..__common__ import *


def cisco_hash(asa):
    def _factory(user=None):
        u = str(user).encode() if user not in (None, "") else b""
        def _hash(text, errors="strict"):
            secret = b(ensure_str(text))
            if len(secret) > (32 if asa else 16):
                raise LookupError("Bad input for encoding 'cisco-%s': password too long" % ("asa" if asa else "pix"))
            # the user name, when there is one, is repeated to 4 bytes and appended (not by the ASA beyond 28 bytes)
            if u and (not asa or len(secret) < 28):
                secret += (u * (4 // len(u) + 1))[:4]
            # pad with null bytes to, or truncate to, 16 bytes (32 for the ASA beyond 16 bytes)
            size = 32 if asa and len(secret) > 16 else 16
            secret = secret[:size].ljust(size, b"\x00")
            digest = hashlib.md5(secret).digest()
            return encode_bytes(bytes(c for i, c in enumerate(digest) if (i + 1) & 3)), len(text)
        return _hash
    return _factory


add("cisco-pix", cisco_hash(False), pattern=r"^cisco[-_]pix(?:[-_](.+))?$", guess=None)
add("cisco-asa", cisco_hash(True), pattern=r"^cisco[-_]asa(?:[-_](.+))?$", guess=None)
