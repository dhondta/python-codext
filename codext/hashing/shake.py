# -*- coding: UTF-8 -*-
"""Case Codecs - string hashing with SHAKE.

These are codecs for hashing strings, for use with other codecs in encoding chains.

These codecs:
- transform strings from str to str
- transform strings from bytes to bytes
- transform file content from str to bytes (write)
"""
import hashlib

from ..__common__ import add, b, PY3


if PY3:
    def shake_hash(i):
        def _hash_transform(l):
            l = (l or str(i)).lstrip("_-")
            def _encode(data, error="strict"):
                return getattr(hashlib, "shake_%d" % i)(b(data)).hexdigest(int(l)), len(data)
            return _encode
        return _hash_transform

    add("shake_128", shake_hash(128), pattern=r"^shake[-_]?128(|[-_][1-9]\d*)$", guess=None)
    add("shake_256", shake_hash(256), pattern=r"^shake[-_]?256(|[-_][1-9]\d*)$", guess=None)

