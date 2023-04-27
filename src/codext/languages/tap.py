# -*- coding: UTF-8 -*-
"""Tap code - Tap/knock code encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


__examples__ = {
    'enc(tap|knock-code|tap_code)': {'this is a test' : ".... ....⠀.. ...⠀.. ....⠀.... ...⠀ ⠀.. ....⠀.... ...⠀ ⠀. ."
                                                        "⠀ ⠀.... ....⠀. .....⠀.... ...⠀.... ...."},
}
__guess__ = ["tap", "tap-inv"]


def __build_encmap(a):
    d, i = {}, 0
    for x in range(1,6): 
        for y in range(1,6): 
            d[a[i]] = x * "." + " " + y * "."
            i += 1
    d['k'], d[' '] = d['c'], " "
    return d



ENCMAP = {
    '':    __build_encmap("abcdefghijlmnopqrstuvwxyz"),
    'inv': __build_encmap("abcdefghijlmnopqrstuvwxyz"[::-1]),
}


add_map("tap", ENCMAP, ignore_case="both", sep="⠀", pattern=r"^(?:tap|knock)(?:[-_]code)?(|inv)$")

