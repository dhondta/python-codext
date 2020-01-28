# -*- coding: UTF-8 -*-
"""Leetspeak Codec - leetspeak content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
try:                 # Python 2
    from string import maketrans
except ImportError:  # Python 3
    maketrans = str.maketrans

from .__common__ import *


alph      = "abeiostABEIOSTZ", "483105748310572"
to_leet   = maketrans(*alph)
from_leet = maketrans(*alph[::-1])


def leet_encode(text, errors="strict"):
    r = text.translate(to_leet)
    return r, len(r)


def leet_decode(text, errors="strict"):
    r = text.translate(from_leet)
    return r, len(r)


add("leet", leet_encode, leet_decode, r"(?:leet|1337|leetspeak)$")
