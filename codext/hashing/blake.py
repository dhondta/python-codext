# -*- coding: UTF-8 -*-
"""Case Codecs - string hashing with blake.

These are codecs for hashing strings, for use with other codecs in encoding chains.

These codecs:
- transform strings from str to str
- transform strings from bytes to bytes
- transform file content from str to bytes (write)
"""
import hashlib

from ..__common__ import add, b, PY3


if PY3:
    def blake_hash(c):
        def _hash_transform(l):
            l = (l or "64" if c == "b" else "32").lstrip("_-")
            def _encode(data, error="strict"):
                return getattr(hashlib, "blake2%s" % c)(b(data), digest_size=int(l)).hexdigest(), len(data)
            return _encode
        return _hash_transform

    add("blake2b", blake_hash("b"), pattern=r"^blake2b(|[-_](?:[1-9]|[1-5]\d|6[0-4]))$", guess=None)
    add("blake2s", blake_hash("s"), pattern=r"^blake2s(|[-_](?:[1-9]|[1-2]\d|3[0-2]))$", guess=None)

