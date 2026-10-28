# -*- coding: UTF-8 -*-
"""MMH3 Codecs - string hashing with MurmurHash3.

MurmurHash3, created by Austin Appleby in 2011, is a fast non-cryptographic hash function used e.g. in hash tables,
 Bloom filters and for fingerprinting (e.g. favicon hashes in Shodan). Its 32-bit and 128-bit variants are provided when
 available in hashlib. These codecs return the hexadecimal digest (one-way), for use with other codecs in encoding
 chains.

These codecs:
- transform strings from str to str
- transform strings from bytes to bytes
- transform file content from str to bytes (write)

Reference: https://github.com/aappleby/smhasher
"""
from ..__common__ import *


if "mmh3_32" in hashlib.algorithms_available:
    add("mmh3_32", lambda s, error="strict": (hashlib.mmh3_32(b(s)).hexdigest(), len(s)), guess=None)
if "mmh3_128" in hashlib.algorithms_available:
    add("mmh3_128", lambda s, error="strict": (hashlib.mmh3_128(b(s)).hexdigest(), len(s)), guess=None)

