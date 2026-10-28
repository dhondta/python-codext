# -*- coding: UTF-8 -*-
"""Shake Hashing Codecs - string hashing with SHAKE.

SHAKE128 and SHAKE256 are the extendable-output functions of the SHA-3 standard (FIPS 202, based on Keccak): the length
 of their output can be chosen, given in bytes in the codec name (e.g. "shake128-32" ; by default, 128 or 256 bytes).
 These codecs return the hexadecimal digest (one-way), for use with other codecs in encoding chains.

These codecs:
- transform strings from str to str
- transform strings from bytes to bytes
- transform file content from str to bytes (write)

Reference: https://csrc.nist.gov/pubs/fips/202/final
"""
from ..__common__ import *


def shake_hash(i):
    def _hash_transform(l):
        l = (l or str(i)).lstrip("_-")
        def _encode(data, error="strict"):
            return getattr(hashlib, "shake_%d" % i)(b(data)).hexdigest(int(l)), len(data)
        return _encode
    return _hash_transform


add("shake_128", shake_hash(128), pattern=r"^shake[-_]?128(|[-_][1-9]\d*)$", guess=None)
add("shake_256", shake_hash(256), pattern=r"^shake[-_]?256(|[-_][1-9]\d*)$", guess=None)

