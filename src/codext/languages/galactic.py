#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Galactic Alphabet Codec - Minecraft enchantment language content encoding.

The Standard Galactic Alphabet was created by Tom Hall for the Commander Keen video games (1990) and later reused as the
 language of Minecraft's enchanting table. Each letter is replaced by Unicode characters resembling its glyph, as most
 online translators (e.g. LingoJam) do: one character for most letters, but "!¡" for p, "ℸ ̣ " (with a combining dot
 below) for t, " ̇/" (with a combining dot above) for x and "||" for y. Other ASCII characters (digits, punctuation,
 whitespace) are kept, except "!" and "|" which cannot be told apart from the letters.

When decoding, several lookalike characters are also accepted for most letters, and the shorter forms of p, t, x and y
 ("!", "ℸ", "̇" and "|"), "!" and "|" being kept as punctuation when the text uses the longer forms. ASCII characters
 (e.g. capital letters, which translators leave unchanged) are kept.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Commander_Keen#Standard_Galactic_Alphabet
"""
from ..__common__ import *


__examples__ = {
    'enc(galactic|minecraft_enchanting_language)': {
        'this is a test': "ℸ ̣ ⍑╎ᓭ ╎ᓭ ᔑ ℸ ̣ ᒷᓭℸ ̣ ",
        'The quick brown fox jumps over the lazy dog.': "ℸ ̣ ⍑ᒷ ᑑ⚍╎ᓵꖌ ʖ∷𝙹∴リ ⎓𝙹 ̇/ ⋮⚍ᒲ!¡ᓭ 𝙹⍊ᒷ∷ ℸ ̣ ⍑ᒷ ꖎᔑ⨅|| ↸𝙹⊣.",
    },
    'enc(galactic-alphabet|minecraft)': {'Bad test!': None, 'été': None},
    'dec(galactic)': {
        # as written by LingoJam, capital letters being left unchanged
        "Sꖎ╎↸ᒷ ℸ ̣ ⍑ᒷ ʖ╎ꖎꖎ ʖᒷℸ ̣ ∴ᒷᒷリ ℸ ̣ ⍑ᒷ ℸ ̣ ∴𝙹 ꖎᒷᔑ⍊ᒷᓭ. T⍑ᒷ ᓭ⍑ᔑꖌ|| ʖᔑ∷リ ⎓ᒷꖎꖎ ∴╎ℸ ̣ ⍑ ᔑ ꖎ𝙹⚍↸ ᓵ∷ᔑᓭ⍑.":
            "Slide the bill between the two leaves. The shaky barn fell with a loud crash.",
        'Mᒷᒷℸ ̣  ᒲᒷ ᔑℸ ̣  ℸ ̣ ⍑ᒷ ᒲᔑ!¡, ℸ ̣ ⍑ᒷ ꖌᒷ|| ᔑリ↸ ᔑ ℸ ̣ 𝙹∷ᓵ⍑!': "Meet me at the map, the key and a torch!",
        # shorter forms and lookalikes
        'ℸ̣⍑ᒷ ᔑ ̇/∷ᔑ||':  "the axray",
        '!ᔑ|':            "pay",
        'ᔑ\u0307/ᒷ ᒷ\u0307':   "axe ex",
        'ℸ₸╎߆ ╎߆ ᒋ ℸᒷ߆ℸ': "this is a test",
        '⍑╎ ̷⠀ᔑ':          "hix a",
        'ᔑ€':             None,
    },
    'enc-dec(galactic)': ["test " + MASKS['l'], "the axe, the text and the toy: 42 apples", "t", "x", "tx yt"],
}


# letters as most online translators write them
ENCMAP = {
    'a': "ᔑ", 'b': "ʖ", 'c': "ᓵ", 'd': "↸", 'e': "ᒷ", 'f': "⎓", 'g': "⊣", 'h': "⍑", 'i': "╎", 'j': "⋮", 'k': "ꖌ",
    'l': "ꖎ", 'm': "ᒲ", 'n': "リ", 'o': "𝙹", 'p': "!¡", 'q': "ᑑ", 'r': "∷", 's': "ᓭ", 't': "ℸ ̣ ", 'u': "⚍", 'v': "⍊",
    'w': "∴", 'x': " ̇/", 'y': "||", 'z': "⨅",
}
# one-character lookalikes accepted when decoding (source: https://shapecatcher.com)
LOOKALIKES = {
    'a': "ᒋᔑ", 'b': "⦣ゝʖ", 'c': "ìᓵ", 'd': "↸", 'e': "ᒷĿ", 'f': "𝌁⎓", 'g': "𐌝┤⫞⊣", 'h': "₸⍑╤", 'i': "╎",
    'j': "⫶⁝ⵗ⋮", 'k': "ꖌ", 'l': "ꖎ", 'm': "ᒲ⟓", 'n': "ソリ", 'o': "⁊フㇷ𝙹", 'p': "ⅱĳ‼", 'q': "ᑑ⊐コ", 'r': "⸬∷⛚",
    's': "߆𝈿ꝇᓭ", 't': "ℸヿ⅂Ꞁ", 'u': "⚍⍨", 'v': "𝍦⍊╧", 'w': "∴⸫⛬", 'x': "ꜘ╱⟋", 'y': "║‖∥ǁ𝄁", 'z': "ᑎ⋂∩⨅⛫",
}
DECMAP = {c: l for l, cs in LOOKALIKES.items() for c in cs}
DOT_BELOW, DOT_ABOVE, LONG_SOLIDUS = "̣", "̇", "̷"


def galactic_encode(text, errors="strict"):
    _h, r = handle_error("galactic", errors), ""
    for i, c in enumerate(ensure_str(text)):
        l = c.lower()
        if l in ENCMAP:
            r += ENCMAP[l]
        elif c.isascii() and c not in "!|" and not c.isalpha():
            r += c
        else:
            r += _h(c, i)
    return r, len(text)


def galactic_decode(text, errors="strict"):
    _h, t, r, i = handle_error("galactic", errors, decode=True), ensure_str(text), "", 0
    # when the longer forms of p, t, x or y are used, a lone "!" or "|" is punctuation
    long_forms = any(f in t for f in ["!¡", DOT_BELOW, DOT_ABOVE + "/", "||"])
    while i < len(t):
        c = t[i]
        if c == "ℸ":
            # "ℸ̣", "ℸ ̣" and "ℸ ̣ " are t, the space following the dot belonging to the letter
            if t[i+1:i+2] == DOT_BELOW:
                i += 1
            elif t[i+1:i+3] == " " + DOT_BELOW:
                i += 3 if t[i+3:i+4] == " " else 2
            r += "t"
        elif c == " " and t[i+1:i+3] == DOT_ABOVE + "/":
            r, i = r + "x", i + 2
        elif c == " " and t[i+1:i+2] == LONG_SOLIDUS:
            r, i = r + "x", i + 1
        elif c == DOT_ABOVE:
            r, i = r + "x", i + (t[i+1:i+2] == "/")
        elif c == "!" and t[i+1:i+2] == "¡":
            r, i = r + "p", i + 1
        elif c == "|" and t[i+1:i+2] == "|":
            r, i = r + "y", i + 1
        elif c in "!|":
            r += c if long_forms else "py"[c == "|"]
        elif c in DECMAP:
            r += DECMAP[c]
        elif c == "⠀":
            r += " "
        elif c.isascii():
            r += c
        else:
            r += _h(c, i)
        i += 1
    return r, len(text)


add("galactic", galactic_encode, galactic_decode, printables_rate=0.,
    pattern=r"^(?:galactic(?:[-_]alphabet)?|minecraft(?:[-_](?:enchantment|enchanting[-_]language))?)$")
