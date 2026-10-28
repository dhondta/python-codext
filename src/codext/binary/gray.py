# -*- coding: UTF-8 -*-
"""Gray Codec - gray code content encoding.

The reflected binary code, patented by Frank Gray in 1953, orders the binary numbers so that two successive values only
 differ by one bit, which avoids spurious intermediate values in electromechanical switches and position encoders. Each
 byte b is replaced by its Gray code b XOR (b >> 1).

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Gray_code
"""
from ..__common__ import *


__examples__ = {
    'enc(gray|reflected-bin|reflected_binary)': {
        'this is a test': "N\\]J0]J0Q0NWJN",
        'THIS IS A TEST': "~lmz0mz0a0~gz~",
   },
}


ENCMAP = {chr(i): chr(i ^ (i >> 1)) for i in range(256)}


add_map("gray", ENCMAP, pattern=r"^(?:gray|reflected[-_]bin(?:ary)?)$", entropy=lambda e: e)

