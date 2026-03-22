# -*- coding: UTF-8 -*-
"""Octal Codec - octal content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


__examples1__ = {
    'enc(octal-spaced|octals_spaced)': {'this is a test': "164 150 151 163 40 151 163 40 141 40 164 145 163 164"},
}
__examples2__ = {
    'enc(octal|octals)': {'this is a test': "164150151163040151163040141040164145163164"},
}


oct2 = lambda i: oct(i).lstrip("0").replace("o", "")

ENCMAP1 = {chr(i): oct2(i) for i in range(256)}
ENCMAP2 = {chr(i): oct2(i).zfill(3) for i in range(256)}


add_map("octal-spaced", ENCMAP1, sep=" ", pattern=r"^octals?[-_]spaced$", examples=__examples1__,
        entropy=lambda e: .07258*e+2.3739, printables_rate=1.)
add_map("octal", ENCMAP2, pattern=r"^octals?$", examples=__examples2__, entropy=lambda e: .08803*e+2.19498,
        printables_rate=1.)

