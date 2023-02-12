#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Galactic Alphabet Codec - Minecraft enchantment language content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


__examples__ = {
    'enc-dec(galactic|minecraft_enchanting_language)': ["test " + MASKS['l']],
    'enc(galactic-alphabet|minecraft)':                {'Bad test#': None},
}


# source: https://shapecatcher.com
ENCMAP = {
    'a': ["ᒋ", "ᔑ"], 'b': ["⦣", "ゝ", "ʖ"], 'c': ["ì", "ᓵ"], 'd': "↸", 'e': ["ᒷ", "Ŀ"], 'f': ["𝌁", "⎓"],
    'g': ["𐌝", "┤", "⫞", "⊣"], 'h': ["₸", "⍑", "╤"], 'i': "╎", 'j': ["⫶", "⁝", "ⵗ", "⋮"], 'k': "ꖌ", 'l': "ꖎ",
    'm': ["ᒲ", "⟓"], 'n': ["ソ", "リ"], 'o': ["⁊", "フ", "ㇷ", "𝙹"], 'p': ["ⅱ", "ĳ", "‼", "!"],
    'q': ["ᑑ", "⊐", "コ"], 'r': ["⸬", "∷", "⛚"], 's': ["߆", "𝈿", "ꝇ", "ᓭ"], 't': ["ℸ", "ヿ", "⅂", "Ꞁ"],
    'u': ["⚍", "⍨"], 'v': ["𝍦", "⍊", "╧"], 'w': ["∴", "⸫", "⛬"], 'x': ["ꜘ", "╱", " ̷", "⟋"],
    'y': ["║", "‖", "∥", "ǁ", "𝄁", "|"], 'z': ["ᑎ", "⋂", "∩", "⨅", "⛫"],
    ' ': [" ", "⠀"],
}


if PY3:
    add_map("galactic", ENCMAP, ignore_case="encode", printables_rate=0.,
            pattern=r"^(?:galactic(?:[-_]alphabet)?|minecraft(?:[-_](?:enchantment|enchanting[-_]language))?)$")

