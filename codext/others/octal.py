# -*- coding: UTF-8 -*-
"""Octal Codec - octal content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


oct2 = lambda i: oct(i).lstrip("0").replace("o", "")

ENCMAP1 = {chr(i): oct2(i) for i in range(256)}
ENCMAP2 = {chr(i): oct2(i).zfill(3) for i in range(256)}


add_map("octal-spaced", ENCMAP1, sep=" ", pattern=r"^octals?[-_]spaced$")
add_map("octal", ENCMAP2, pattern=r"^octals?$")
