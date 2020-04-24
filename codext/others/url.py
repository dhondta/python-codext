# -*- coding: UTF-8 -*-
"""URL Codec - urlencode content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


SAFE = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-"
ENCMAP = {}
for i in range(256):
    c = chr(i)
    if c not in SAFE:
        ENCMAP[c] = "%{:02X}".format(i)


add_map("url", ENCMAP, ignore_case="decode", no_error=True, pattern=r"^url(?:encode)?$")
