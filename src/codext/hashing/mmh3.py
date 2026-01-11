# -*- coding: UTF-8 -*-
"""MMH3 Codecs - string hashing with MurmurHash3.

These are codecs for hashing strings, for use with other codecs in encoding chains.

These codecs:
- transform strings from str to str
- transform strings from bytes to bytes
- transform file content from str to bytes (write)
"""
from ..__common__ import *


if "mmh3_32" in hashlib.algorithms_available:
    add("mmh3_32", lambda s, error="strict": (hashlib.mmh3_32(b(s)).hexdigest(), len(s)), guess=None)
if "mmh3_128" in hashlib.algorithms_available:
    add("mmh3_128", lambda s, error="strict": (hashlib.mmh3_128(b(s)).hexdigest(), len(s)), guess=None)

