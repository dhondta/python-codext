# -*- coding: UTF-8 -*-
"""Adler Codecs - Adler32 checksum algorithm.

Adler-32 was designed by Mark Adler in 1995 for zlib, as a faster alternative to CRC-32: it is made of two 16-bit sums
 modulo 65521 (the largest prime below 2^16), one of the bytes and one of the successive values of the first sum,
 combined into a 32-bit integer. This codec computes it (one-way), for use with other codecs in encoding chains.

This codec:
- transforms strings from str to str
- transforms strings from bytes to bytes
- transforms file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Adler-32
"""
from zlib import adler32

from ..__common__ import add, b


add("adler32", lambda data, error="strict": (adler32(b(data)) & 0xffffffff, len(data)), guess=None)

