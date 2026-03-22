# -*- coding: UTF-8 -*-
"""Klopf Codec - Polybius-based content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


__examples__ = {
    'enc(klopf|klopfcode)': {'this is a test': "44324234 4234 11 44513444"},
}


ENCMAP = {"ABCDEFGHIKLMNOPQRSTUVWXYZ"[y*5+x]: "".join([str(x+1), str(y+1)]) for x in range(5) for y in range(5)}
ENCMAP['J'] = "43"
ENCMAP[' '] = " "


add_map("klopf", ENCMAP, ignore_case="both", pattern=r"^(?:klopf(?:code)?)$", printables_rate=1.,
        expansion_factor=(1.85, .15))

