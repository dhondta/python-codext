# -*- coding: UTF-8 -*-
"""Case Codecs - string hashing with Secure Hash Algorithms.

These are codecs for hashing strings, for use with other codecs in encoding chains.

These codecs:
- transform strings from str to str
- transform strings from bytes to bytes
- transform file content from str to bytes (write)
"""
import hashlib

from ..__common__ import add, b, PY3


add("sha1", lambda s, error="strict": (hashlib.sha1(b(s)).hexdigest(), len(s)), guess=None)
add("sha224", lambda s, error="strict": (hashlib.sha224(b(s)).hexdigest(), len(s)), guess=None)
add("sha256", lambda s, error="strict": (hashlib.sha256(b(s)).hexdigest(), len(s)), guess=None)
add("sha384", lambda s, error="strict": (hashlib.sha384(b(s)).hexdigest(), len(s)), guess=None)
add("sha512", lambda s, error="strict": (hashlib.sha512(b(s)).hexdigest(), len(s)), guess=None)


if PY3:
    add("sha3_224", lambda s, error="strict": (hashlib.sha3_224(b(s)).hexdigest(), len(s)), pattern=r"^sha3[-_]224$",
        guess=None)
    add("sha3_256", lambda s, error="strict": (hashlib.sha3_256(b(s)).hexdigest(), len(s)), pattern=r"^sha3[-_]256$",
        guess=None)
    add("sha3_384", lambda s, error="strict": (hashlib.sha3_384(b(s)).hexdigest(), len(s)), pattern=r"^sha3[-_]384$",
        guess=None)
    add("sha3_512", lambda s, error="strict": (hashlib.sha3_512(b(s)).hexdigest(), len(s)), pattern=r"^sha3[-_]512$",
        guess=None)

