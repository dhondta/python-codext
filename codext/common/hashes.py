# -*- coding: UTF-8 -*-
"""Case Codecs - string hashing.

These are codecs for hashing strings, for use with other codecs in encoding chains.

These codecs:
- transform strings from str to str
- transform strings from bytes to bytes
- transform file content from str to bytes (write)
"""
import hashlib

from ..__common__ import add, b, PY3


# Python2/3-compatible hash functions
add("md5", lambda s, error="strict": (hashlib.md5(b(s)).hexdigest(), len(s)), guess=None)
add("sha1", lambda s, error="strict": (hashlib.sha1(b(s)).hexdigest(), len(s)), guess=None)
add("sha224", lambda s, error="strict": (hashlib.sha224(b(s)).hexdigest(), len(s)), guess=None)
add("sha256", lambda s, error="strict": (hashlib.sha256(b(s)).hexdigest(), len(s)), guess=None)
add("sha384", lambda s, error="strict": (hashlib.sha384(b(s)).hexdigest(), len(s)), guess=None)
add("sha512", lambda s, error="strict": (hashlib.sha512(b(s)).hexdigest(), len(s)), guess=None)


# Python3 only
if PY3:
    def blake_hash(c):
        def _hash_transform(l):
            l = (l or "64").lstrip("_-")
            def _encode(data, error="strict"):
                return getattr(hashlib, "blake2%s" % c)(b(data), digest_size=int(l)).hexdigest(), len(data)
            return _encode
        return _hash_transform

    add("blake2b", blake_hash("b"), pattern=r"^blake2b(|[-_](?:[1-9]|[1-5]\d|6[0-4]))$", guess=None)
    add("blake2s", blake_hash("s"), pattern=r"^blake2s(|[-_](?:[1-9]|[1-2]\d|3[0-2]))$", guess=None)

    def shake_hash(i):
        def _hash_transform(l):
            l = (l or str(i)).lstrip("_-")
            def _encode(data, error="strict"):
                return getattr(hashlib, "shake_%d" % i)(b(data)).hexdigest(int(l)), len(data)
            return _encode
        return _hash_transform

    add("shake_128", shake_hash(128), pattern=r"^shake[-_]?128(|[-_][1-9]\d*)$", guess=None)
    add("shake_256", shake_hash(256), pattern=r"^shake[-_]?256(|[-_][1-9]\d*)$", guess=None)

    add("sha3_224", lambda s, error="strict": (hashlib.sha3_224(b(s)).hexdigest(), len(s)), pattern=r"^sha3[-_]224$",
        guess=None)
    add("sha3_256", lambda s, error="strict": (hashlib.sha3_256(b(s)).hexdigest(), len(s)), pattern=r"^sha3[-_]256$",
        guess=None)
    add("sha3_384", lambda s, error="strict": (hashlib.sha3_384(b(s)).hexdigest(), len(s)), pattern=r"^sha3[-_]384$",
        guess=None)
    add("sha3_512", lambda s, error="strict": (hashlib.sha3_512(b(s)).hexdigest(), len(s)), pattern=r"^sha3[-_]512$",
        guess=None)

