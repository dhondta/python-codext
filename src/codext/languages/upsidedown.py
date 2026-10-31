# -*- coding: UTF-8 -*-
"""Upside-down Codec - upside-down (flip) text content encoding.

Upside-down text (aka flip text) is written with Unicode characters that look like the letters, digits and punctuation
 turned by 180 degrees (mostly from the IPA, Lisu and Letterlike Symbols blocks, e.g. "ɐ" for "a", "ꓭ" for "B" or "¿"
 for "?"), in reverse order, so that the text reads normally when turned upside down. Some characters are their own
 turned versions (e.g. "o", "s", "x", "H" or "8") or the turned version of each other (e.g. "b" and "q", "n" and "u",
 "M" and "W", "6" and "9" or the brackets), and the table pairs every character with its turned version, hence turning
 the text twice gives it back: encoding and decoding are the same operation. Decoding also accepts other characters
 used by the online generators (e.g. "∀" for "A", "˥" for "L" or "∩" for "U"). The other characters are kept as is.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Transformation_of_text#Upside-down_text
"""
from ..__common__ import *


__examples__ = {
    'enc(upsidedown|upside-down|upside_down|flip-text|fliptext)': {
        'Hello, World!': "\xa1pꞁɹoM 'oꞁꞁǝH", 'hello world': "pꞁɹoʍ oꞁꞁǝɥ",
    },
    'dec(upsidedown)': {"\xa1pꞁɹoM '∀": "A, World!"},
    'enc-dec(upsidedown)': ["", "The quick brown fox jumps over the lazy dog: 0123456789 (&) [?] {!} <_> \"'.,;",
                            "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG", "caf\xe9 €"],
}


# characters with their turned versions (based on the table of Wikipedia, with single characters, the M/W pair and the
#  Lisu U, and the digits of the online generators), each pair being used in both directions
_PAIRS = [
    ("a", "ɐ"), ("b", "q"), ("c", "ɔ"), ("d", "p"), ("e", "ǝ"), ("f", "ɟ"), ("g", "ᵷ"), ("h", "ɥ"), ("i", "ᴉ"),
    ("j", "ɾ"), ("k", "ʞ"), ("l", "ꞁ"), ("m", "ɯ"), ("n", "u"), ("r", "ɹ"), ("t", "ʇ"), ("v", "ʌ"), ("w", "ʍ"),
    ("y", "ʎ"), ("A", "Ɐ"), ("B", "ꓭ"), ("C", "Ɔ"), ("D", "ꓷ"), ("E", "Ǝ"), ("F", "Ⅎ"), ("G", "⅁"), ("J", "ꓩ"),
    ("K", "Ʞ"), ("L", "Ꞁ"), ("M", "W"), ("P", "Ԁ"), ("Q", "Ꝺ"), ("R", "ꓤ"), ("T", "Ʇ"), ("U", "ꓵ"), ("V", "Ʌ"),
    ("Y", "⅄"), ("1", "Ɩ"), ("2", "↊"), ("3", "↋"), ("4", "ㄣ"), ("5", "ϛ"), ("6", "9"), ("7", "ㄥ"), ("&", "⅋"),
    ("_", "‾"), ("?", "¿"), ("!", "¡"), ('"', "„"), ("'", ","), (".", "˙"), (";", "؛"), ("(", ")"), ("[", "]"),
    ("{", "}"), ("<", ">"),
]
# other turned versions used by the online generators, only decoded
_VARIANTS = {
    "ı": "i", "ן": "l", "ƃ": "g", "ɓ": "g", "∀": "A", "ꓯ": "A", "𐐒": "B", "ꓛ": "C", "ꓱ": "E", "ꓞ": "F", "ꓨ": "G",
    "ſ": "J", "ꓘ": "K", "˥": "L", "⅂": "L", "ꓶ": "L", "ꟽ": "M", "ꓒ": "P", "ꓕ": "T", "⊥": "T", "∩": "U", "Ո": "U",
    "Λ": "V", "ꓥ": "V", "𐤵": "W", "ᄅ": "2", "Ɛ": "3", "߈": "4", "𝘓": "7", "\U0001fbf1": "1", "\U0001fbf5": "5",
}
UPSIDE_DOWN = {**{a: b for a, b in _PAIRS}, **{b: a for a, b in _PAIRS}, **_VARIANTS}


def upsidedown(text, errors="strict"):
    return "".join(UPSIDE_DOWN.get(c, c) for c in reversed(ensure_str(text))), len(text)


add("upsidedown", upsidedown, upsidedown, r"^(?:upside[-_]?down|flip[-_]?text)$", examples=__examples__,
    guess=None)
