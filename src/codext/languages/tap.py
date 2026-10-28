# -*- coding: UTF-8 -*-
"""Tap code - Tap/knock code encoding.

The tap code (or knock code), used by prisoners of war (e.g. in Vietnam) to communicate by tapping on walls, writes each
 letter as its row and column in a 5x5 Polybius square, K being replaced by C. Each coordinate is written as dots (taps)
 separated by a space, the letters being separated by the blank braille pattern ; the "-inv" variant uses the reversed
 alphabet.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Tap_code
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

