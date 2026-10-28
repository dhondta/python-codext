# -*- coding: UTF-8 -*-
"""FNV Codecs - string hashing with Fowler-Noll-Vo.

The Fowler-Noll-Vo hash functions were designed by Glenn Fowler, Landon Curt Noll and Kiem-Phong Vo in 1991. They are
 fast non-cryptographic hash functions, used e.g. in hash tables and checksums. Starting from an offset basis, each byte
 of the data is combined with the hash value, which is then multiplied by a prime, modulo 2^N:
- FNV-1 multiplies first, then XORes the byte
- FNV-1a XORes the byte first, then multiplies (better avalanche on short inputs)

The width N (32, 64, 128, 256, 512 or 1024 bits) is given with the codec name (e.g. "fnv1a-64") ; it defaults to 32. The
 offset basis of each width is the FNV-0 hash (that is, FNV-1 with an offset basis of 0) of the string
 "chongo <Landon Curt Noll> /\\../\\". These codecs return the zero-padded hexadecimal digest (one-way), for use with
 other codecs in encoding chains.

These codecs:
- transform strings from str to str
- transform strings from bytes to bytes
- transform file content from str to bytes (write)

Reference: http://www.isthe.com/chongo/tech/comp/fnv/index.html
"""
from ..__common__ import *


# primes per width, as 2^x + 2^8 + y
PRIMES = {32: 2**24 + 0x193, 64: 2**40 + 0x1b3, 128: 2**88 + 0x13b, 256: 2**168 + 0x163, 512: 2**344 + 0x157,
          1024: 2**680 + 0x18d}


def __fnv(data, n, offset, xor_first=False):
    h, p, m = offset, PRIMES[n], (1 << n) - 1
    for x in data:
        if xor_first:
            h ^= x
        h = h * p & m
        if not xor_first:
            h ^= x
    return h


OFFSETS = {n: __fnv(b"chongo <Landon Curt Noll> /\\../\\", n, 0) for n in PRIMES}


def fnv(xor_first=False):
    def _wrapper(n=""):
        # a bad width is only reported when coding, as the lookup of the bare codec name must succeed (e.g. when listing
        #  the encodings)
        n = n or 32
        def _hash(data, errors="strict"):
            if n not in PRIMES:
                raise LookupError("Bad parameter for encoding 'fnv': width must be one of "
                                  f"{', '.join(map(str, PRIMES))}")
            return f"{__fnv(b(data), n, OFFSETS[n], xor_first):0{n // 4}x}", len(data)
        return _hash
    return _wrapper


add("fnv1", fnv(), pattern=r"^fnv[-_]?1(?:[-_](\d+))?$", guess=None)
add("fnv1a", fnv(True), pattern=r"^fnv[-_]?1a(?:[-_](\d+))?$", guess=None)
