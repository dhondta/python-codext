# -*- coding: UTF-8 -*-
"""Whitespace Codec - whitespace/tabs content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


ENCMAP = {r'': {'0': "\t", '1': " "}, r'[-_]inv(erted)?': {'0': " ", '1': "\t"}}


add_map("whitespace", ENCMAP, binary=True, pattern=r"^whitespace(?:s)?([-_]inv(?:erted)?)?$")
