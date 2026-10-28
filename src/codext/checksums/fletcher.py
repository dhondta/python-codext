# -*- coding: UTF-8 -*-
"""Fletcher Codecs - Fletcher-16/32/64 checksum algorithm.

The Fletcher checksum was designed by John G. Fletcher in the late 1970s, as an alternative to CRCs that is cheaper to
 compute while detecting errors in their position (unlike a simple sum). The data is cut into blocks of 8, 16 or 32 bits
 (little-endian, the last block being padded with zero bytes), then two sums are computed modulo 2^8-1, 2^16-1 or
 2^32-1: one of the blocks and one of the successive values of the first sum. They are combined into a 16-, 32- or
 64-bit integer, with the second sum in the most significant half.

The width is given with the codec name (e.g. "fletcher32") ; it defaults to 16. This codec returns the zero-padded
 hexadecimal checksum (one-way), for use with other codecs in encoding chains.

This codec:
- transforms strings from str to str
- transforms strings from bytes to bytes
- transforms file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Fletcher%27s_checksum
"""
from ..__common__ import *


def fletcher(n=""):
    # a bad width is only reported when coding, as the lookup of the bare codec name must succeed (e.g. when listing
    #  the encodings)
    n = n or 16
    def _checksum(data, errors="strict"):
        if n not in (16, 32, 64):
            raise LookupError("Bad parameter for encoding 'fletcher': width must be 16, 32 or 64")
        d, k = b(data), n // 16
        d, m, s1, s2 = d + b"\x00" * (-len(d) % k), (1 << n // 2) - 1, 0, 0
        for i in range(0, len(d), k):
            s1 = (s1 + int.from_bytes(d[i:i+k], "little")) % m
            s2 = (s2 + s1) % m
        return f"{s2 << n // 2 | s1:0{n // 4}x}", len(data)
    return _checksum


add("fletcher", fletcher, pattern=r"^fletcher(?:[-_]?(\d+))?$", guess=None)
