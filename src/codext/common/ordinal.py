# -*- coding: UTF-8 -*-
"""Ordinal Codec - ordinal content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


__examples1__ = {
    'enc(ordinal-spaced|ordinals_spaced)': {'this is a test': "116 104 105 115 32 105 115 32 97 32 116 101 115 116"},
}
__examples2__ = {
    'enc(ordinal|ordinals)': {'this is a test': "116104105115032105115032097032116101115116"},
}


ENCMAP1 = {chr(i): str(i) for i in range(256)}
ENCMAP2 = {chr(i): str(i).zfill(3) for i in range(256)}


add_map("ordinal-spaced", ENCMAP1, sep=" ", pattern=r"^ordinals?[-_]spaced$", examples=__examples1__, entropy=3.,
        printables_rate=1.)
add_map("ordinal", ENCMAP2, pattern=r"^ordinals?$", examples=__examples2__, entropy=3., printables_rate=1.)

