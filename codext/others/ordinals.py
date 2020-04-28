# -*- coding: UTF-8 -*-
"""Ordinals Codec - ordinals content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


ENCMAP = {chr(i): str(i) for i in range(256)}


add_map("ordinals", ENCMAP, sep=" ", pattern=r"^ordinals?$")
