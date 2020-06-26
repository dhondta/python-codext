# -*- coding: UTF-8 -*-
"""Ordinal Codec - ordinal content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


ENCMAP1 = {chr(i): str(i) for i in range(256)}
ENCMAP2 = {chr(i): str(i).zfill(3) for i in range(256)}


add_map("ordinal-spaced", ENCMAP1, sep=" ", pattern=r"^ordinals?[-_]spaced$")
add_map("ordinal", ENCMAP2, pattern=r"^ordinals?$")
