# -*- coding: UTF-8 -*-
"""Adler Codecs - Adler32 checksum algorithm.

This is a codec for computing checksums, for use with other codecs in encoding chains.

These codecs:
- transform strings from str to str
- transform strings from bytes to bytes
- transform file content from str to bytes (write)
"""
from zlib import adler32

from ..__common__ import add, b


add("adler32", lambda data, error="strict": (adler32(b(data)) & 0xffffffff, len(data)), guess=None)

