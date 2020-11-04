# -*- coding: UTF-8 -*-
"""Leetspeak Codec - leetspeak content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


__examples__ = {
    'enc(leet|1337|leetspeak)': {'this is a test': "7h15 15 4 7357"},
    'dec(leet|1337|leetspeak)': {'7H15 15 4 7357': "THIS IS A TEST"},
}


ENCMAP = {k: v for k, v in zip("abeiostz", "48310572")}


add_map("leet", ENCMAP, ignore_case="encode", no_error=True, pattern=r"(?:leet|1337|leetspeak)$")

