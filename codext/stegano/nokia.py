# -*- coding: UTF-8 -*-
"""Nokia Codec - nokia keystrokes content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


ENCMAP = {
    ' ': "0", 'a': "2", 'c': "222", 'b': "22", 'e': "33", 'd': "3", 'g': "4", 'f': "333", 'i': "444", 'h': "44",
    'k': "55", 'j': "5", 'm': "6", 'l': "555", 'o': "666", 'n': "66", 'q': "77", 'p': "7", 's': "7777", 'r': "777",
    'u': "88", 't': "8", 'w': "9", 'v': "888", 'y': "999", 'x': "99", 'z': "9999",
}


add_map("nokia", ENCMAP, "?", "-_", ignore_case="encode", pattern=r"^nokia[-_]?3310$")
