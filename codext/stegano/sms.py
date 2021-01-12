# -*- coding: UTF-8 -*-
"""SMS Codec - phone keystrokes content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


__examples__ = {
    'enc(sms|nokia3310|nokia-3310|nokia_3310|t9)': {'this is a test': "8-44-444-7777-0-444-7777-0-2-0-8-33-7777-8"},
}


ENCMAP = {
    ' ': "0", 'a': "2", 'b': "22", 'c': "222", 'd': "3", 'e': "33", 'f': "333", 'g': "4", 'h': "44", 'i': "444",
    'j': "5", 'k': "55", 'l': "555", 'm': "6", 'n': "66", 'o': "666", 'p': "7", 'q': "77", 'r': "777", 's': "7777",
    't': "8", 'u': "88", 'v': "888", 'w': "9", 'x': "99", 'y': "999", 'z': "9999", '*': "*", '#': "#",
}


add_map("sms", ENCMAP, "?", "-_", ignore_case="encode", pattern=r"^(?:nokia(?:[-_]?3310)?|sms|t9)$", printables_rate=1.)

