#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Galactic Alphabet Codec - Minecraft enchantment language content encoding.

The Standard Galactic Alphabet was created by Tom Hall for the Commander Keen video games (1990) and later reused as the
 language of Minecraft's enchanting table. Each letter is replaced by a Unicode character resembling its glyph ; as
 there are no exact Unicode equivalents, several lookalike characters are accepted for most letters when decoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Commander_Keen#Standard_Galactic_Alphabet
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


add_map("galactic", ENCMAP, ignore_case="encode", printables_rate=0.,
        pattern=r"^(?:galactic(?:[-_]alphabet)?|minecraft(?:[-_](?:enchantment|enchanting[-_]language))?)$")

