# -*- coding: UTF-8 -*-
"""ROT-N Codec - rotN content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from string import ascii_lowercase as LC, ascii_uppercase as UC
try:                 # Python 2
    from string import maketrans
except ImportError:  # Python 3
    maketrans = str.maketrans

from .__common__ import *


def _rotn(text, n=13):
    n = n % 26
    t = maketrans(LC + UC, LC[n:] + LC[:n] + UC[n:] + UC[:n])
    return text.translate(t)


def rot_encode(i):
    def encode(text, errors="strict"):
        r = _rotn(ensure_str(text), i)
        return r, len(r)
    return encode


def rot_decode(i):
    def decode(text, errors="strict"):
        r = _rotn(ensure_str(text), -i)
        return r, len(r)
    return decode


# note: the integer behind "rot" is captured for sending to the parametrizable
#        encode and decode functions "rotn_**code"
add("rotN", rot_encode, rot_decode, r"(?i)rot[-_]?([1-9]|1[0-9]|2[0-5])$")
