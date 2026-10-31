# -*- coding: UTF-8 -*-
"""Fancy Codecs - Unicode styled alphabets content encoding.

Unicode has styled versions of the Latin letters and of the digits, often used to write "fancy" text (e.g. in social
 networks) or to obfuscate text (e.g. to evade filters): the mathematical alphanumeric symbols (bold, italic, bold
 italic, script, bold script, fraktur, bold fraktur, double-struck, sans-serif, sans-serif bold, sans-serif italic,
 sans-serif bold italic and monospace, some letters being in the Letterlike Symbols block, e.g. "ℬ" or "ℎ"), the
 circled and parenthesized letters and digits, the full-width forms of ASCII and the small capitals (for the lowercase
 letters, except "x" that has no small capital). Encoding writes the letters and digits of the text in the given style
 (or, for full-width forms, all the printable ASCII characters, and the space as an ideographic space), keeping the
 other characters, while decoding writes back the characters of this style ; "fancy" without a style decodes all of
 them at once (e.g. for text mixing several styles).

The NFKC normalization (unicodedata.normalize("NFKC", ...)) also undoes the mathematical, circled and full-width styles,
 but not the parenthesized one (giving e.g. "(a)") nor the small capitals ; unlike this codec, it changes other
 characters as well (e.g. ligatures and superscripts).

These codecs:
- en/decode strings from str to str
- en/decode strings from bytes to bytes
- decode file content to str (read)
- encode file content from str to bytes (write)

Reference: https://www.unicode.org/charts/PDF/U1D400.pdf
"""
import unicodedata
from string import ascii_lowercase, ascii_uppercase, digits

from ..__common__ import *


__examples1__ = {
    'enc(fancy-bold|fancy_bold)': {'Hello 2026!': "\U0001d407\U0001d41e\U0001d425\U0001d425\U0001d428 \U0001d7d0"
                                                  "\U0001d7ce\U0001d7d0\U0001d7d4!"},
    'enc(fancy-script)': {'Bohe': "ℬℴ\U0001d4bdℯ"},
    'dec(fancy)': {'\U0001d407\U0001d58a\U0001d695ⓛ⒪ ｗᴏʀʟᴅ': "Hello world"},
    'enc-dec(fancy-%s)': ["", "Hello World 2026", "caf\xe9 & €, 日本!"],
}
__examples2__ = {
    'enc(fullwidth|full-width|full_width)': {'Hello, World!': "Ｈｅｌｌｏ，\u3000Ｗｏ"
                                                              "ｒｌｄ！"},
    'enc-dec(fullwidth)': ["", "@random{256}"],
}
__examples3__ = {
    'enc(smallcaps|small-caps|small_caps)': {'Hello World': "Hᴇʟʟᴏ Wᴏʀʟᴅ"},
    'enc-dec(smallcaps)': ["", "The quick brown fox jumps over the lazy dog", "@random{256}"],
}


_DIGITS = ["ZERO", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE"]
# names of the letters of some styles that are in the Letterlike Symbols block (e.g. "SCRIPT CAPITAL B")
_LETTERLIKE = {'SCRIPT': "SCRIPT", 'FRAKTUR': "BLACK-LETTER", 'DOUBLE-STRUCK': "DOUBLE-STRUCK"}


def _lookup(*names):
    """ First character with one of the given names (the characters missing from the Unicode database of the version of
         Python being skipped). """
    for name in names:
        try:
            return unicodedata.lookup(name)
        except KeyError:
            pass


def __alphabet(name, chars):
    return {c: f for c in chars if (f := _lookup(*name(c)))}


def __math(style):
    case = lambda c: "CAPITAL" if c.isupper() else "SMALL"
    return __alphabet(lambda c: [f"MATHEMATICAL {style} DIGIT {_DIGITS[int(c)]}"] if c.isdigit() else
                      [f"MATHEMATICAL {style} {case(c)} {c.upper()}"] +
                      ([f"{_LETTERLIKE[style]} {case(c)} {c.upper()}"] if style in _LETTERLIKE else []) +
                      ["PLANCK CONSTANT"] * (style == "ITALIC" and c == "h"),
                      ascii_uppercase + ascii_lowercase + digits)


def __enclosed(kind):
    return __alphabet(lambda c: [f"{kind} DIGIT {_DIGITS[int(c)]}"] if c.isdigit() else
                      [f"{kind} LATIN {'CAPITAL' if c.isupper() else 'SMALL'} LETTER {c.upper()}"],
                      ascii_uppercase + ascii_lowercase + digits)


ALPHABETS = {s.lower().replace(" ", "-"): __math(s) for s in ["BOLD", "ITALIC", "BOLD ITALIC", "SCRIPT", "BOLD SCRIPT",
             "FRAKTUR", "BOLD FRAKTUR", "DOUBLE-STRUCK", "SANS-SERIF", "SANS-SERIF BOLD", "SANS-SERIF ITALIC",
             "SANS-SERIF BOLD ITALIC", "MONOSPACE"]}
ALPHABETS.update({
    'circled':       __enclosed("CIRCLED"),
    'parenthesized': __enclosed("PARENTHESIZED"),
    'fullwidth':     {chr(i): chr(i + 0xfee0) for i in range(0x21, 0x7f)} | {" ": "\u3000"},
    'smallcaps':     __alphabet(lambda c: [f"LATIN LETTER SMALL CAPITAL {c.upper()}"], ascii_lowercase),
})
DECODE = {k: {f: c for c, f in a.items()} for k, a in ALPHABETS.items()}
DECODE_ALL = {f: c for d in DECODE.values() for f, c in d.items()}
__examples1__["enc-dec(fancy-%s)" % "|fancy-".join(ALPHABETS)] = __examples1__.pop("enc-dec(fancy-%s)")


def fancy_encode(style=None):
    def encode(text, errors="strict"):
        if not style:
            raise LookupError("Bad parameter for encoding 'fancy': a style is required, among " + ", ".join(ALPHABETS))
        alphabet = ALPHABETS[style.replace("_", "-")]
        return "".join(alphabet.get(c, c) for c in ensure_str(text)), len(text)
    return encode


def fancy_decode(style=None):
    def decode(text, errors="strict"):
        table = DECODE[style.replace("_", "-")] if style else DECODE_ALL
        return "".join(table.get(c, c) for c in ensure_str(text)), len(text)
    return decode


add("fancy", fancy_encode, fancy_decode, r"^fancy(?:[-_](" + "|".join(s.replace("-", "[-_]") for s in ALPHABETS) +
    r"))?$", examples=__examples1__, guess=None)
add("fullwidth", fancy_encode("fullwidth"), fancy_decode("fullwidth"), r"^full[-_]?width$", examples=__examples2__,
    guess=None)
add("smallcaps", fancy_encode("smallcaps"), fancy_decode("smallcaps"), r"^small[-_]?caps$", examples=__examples3__,
    guess=None)
