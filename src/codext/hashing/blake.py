# -*- coding: UTF-8 -*-
"""Blake2 Codecs - string hashing with blake.

BLAKE2, designed by Jean-Philippe Aumasson, Samuel Neves, Zooko Wilcox-O'Hearn and Christian Winnerlein in 2012 and
 derived from the SHA-3 finalist BLAKE, is a cryptographic hash function faster than MD5 and SHA-2. It comes in two
 flavours: BLAKE2b (64-bit platforms, digests of 1 to 64 bytes) and BLAKE2s (8- to 32-bit platforms, digests of 1 to 32
 bytes), the digest size being given in the codec name (e.g. "blake2b-32"). These codecs return the hexadecimal digest
 (one-way), for use with other codecs in encoding chains.

These codecs:
- transform strings from str to str
- transform strings from bytes to bytes
- transform file content from str to bytes (write)

Reference: https://datatracker.ietf.org/doc/html/rfc7693
"""
from ..__common__ import *


def blake_hash(c):
    def _hash_transform(l):
        l = (l or "64" if c == "b" else "32").lstrip("_-")
        def _encode(data, error="strict"):
            return getattr(hashlib, "blake2%s" % c)(b(data), digest_size=int(l)).hexdigest(), len(data)
        return _encode
    return _hash_transform


add("blake2b", blake_hash("b"), pattern=r"^blake2b(|[-_](?:[1-9]|[1-5]\d|6[0-4]))$", guess=None)
add("blake2s", blake_hash("s"), pattern=r"^blake2s(|[-_](?:[1-9]|[1-2]\d|3[0-2]))$", guess=None)

