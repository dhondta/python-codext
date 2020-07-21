# -*- coding: UTF-8 -*-
"""Base122 Codec - base122 content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


def base122_encode(input, errors="strict"):
    raise NotImplementedError


def base122_decode(input, errors="strict"):
    raise NotImplementedError


add("base122", base122_encode, base122_decode, r"^base[-_]?122$")

