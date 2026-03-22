# -*- coding: UTF-8 -*-
"""URL Codec - urlencode content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


__examples__ = {
    'enc(url|urlencode)': {'?=this/is-a_test/../': "%3F%3Dthis%2Fis-a_test%2F%2E%2E%2F"},
    'dec(url|urlencode)': {'test/test%2etxt': "test/test.txt", 'test%2ftest.txt': "test/test.txt"}
}


SAFE = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-"
ENCMAP = {}
for i in range(256):
    c = chr(i)
    if c not in SAFE:
        ENCMAP[c] = "%{:02X}".format(i)


add_map("url", ENCMAP, ignore_case="decode", no_error=True, pattern=r"^url(?:encode)?$", printables_rate=1.,
        expansion_factor=(1.2, .2))

