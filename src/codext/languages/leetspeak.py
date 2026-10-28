# -*- coding: UTF-8 -*-
"""Leetspeak Codec - leetspeak content encoding.

Leetspeak (1337), born in the 1980s on bulletin board systems, replaces letters by similar-looking digits or symbols.
 This codec uses the substitutions A=4 (or @), B=8, E=3, G=9, I=1, L=1, O=0, S=5, T=7 and Z=2 ; as several letters share
 the same symbol, decoding is ambiguous and outputs uppercase letters.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Leet
"""
from ..__common__ import *


__examples__ = {
    'enc(leet|1337|leetspeak)': {'this is a test': "7h15 15 4 7357"},
    'dec(leet|1337|leetspeak)': {'7H15 15 4 7357': "THIS IS A TEST"},
}


ENCMAP = {k: v for k, v in zip("aabeliostzg", "@4831105729")}


add_map("leet", ENCMAP, ignore_case="encode", no_error=True, pattern=r"(?:leet|1337|leetspeak)$", entropy=lambda e: e)

