# -*- coding: UTF-8 -*-
"""Zero-Width Codec - zero-width characters content encoding.

This codec hides text in invisible Unicode characters. The encoded string can then be inserted anywhere in a cover text
 as, when decoding, every character that is not part of the zero-width alphabet is ignored.

Three variants are supported:
- binary (default): the UTF-8 bytes are written as bits, ZERO WIDTH SPACE (U+200B) for 0 and ZERO WIDTH NON-JOINER
   (U+200C) for 1
- ternary: each code point is written with 11 digits in base 3 (U+200B, U+200C, ZERO WIDTH JOINER U+200D) ; this is
   the MODE_ZWSP of zwsp-steg
- quinary: each code point is written with 7 digits in base 5 (U+200B, U+200C, U+200D, LEFT-TO-RIGHT MARK U+200E,
   RIGHT-TO-LEFT MARK U+200F) ; this is the MODE_FULL of zwsp-steg

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://github.com/enodari/zwsp-steg-py
"""
from ..__common__ import *


__examples__ = {
    'enc(zero-width|zerowidth|zero_width-binary|zero-width-2)': {'A': "\u200b\u200c" + "\u200b" * 5 + "\u200c"},
    'enc(zero-width-ternary|zero-width-zwsp|zero-width-3)':     {'A': "\u200b" * 7 + "\u200d\u200c\u200b\u200d"},
    'enc(zero-width-quinary|zero-width-full|zero-width-5)':     {'A': "\u200b" * 4 + "\u200d\u200e\u200b"},
    'enc(zero-width-ternary)':                                  {'A\U0010ffff': None},
    'enc(zero-width-quinary)':                                  {'A\U0001f600': None},
    'dec(zero-width)':                                          {'\u200b\u200c\u200b': None, '\u200c' * 8: None},
    'dec(zero-width-ternary)':                                  {'\u200d' * 10: None},
    'dec(zero-width-quinary)':                                  {'\u200b' * 6: None},
    'dec(zero-width-full)':                                     {'Hello\u200b\u200b\u200b\u200b\u200d\u200e\u200b'
                                                                 ' World': "A"},
    'enc-dec(zero-width)':                                      ["Hello, World!", "Caf\u00e9 \u2713 \U0001f600",
                                                                 "@random"],
    'enc-dec(zero-width-ternary)':                              ["Hello, World!", "Caf\u00e9 \u2713 \U0001f600",
                                                                 "@random"],
    'enc-dec(zero-width-quinary)':                              ["Hello, World!", "Caf\u00e9 \u2713", "@random"],
}
__guess__ = ["zero-width", "zero-width-ternary", "zero-width-quinary"]


ZWSP, ZWNJ, ZWJ, LRM, RLM = "\u200b", "\u200c", "\u200d", "\u200e", "\u200f"
# variant: (alphabet, number of digits per code point ; None means 8 bits per UTF-8 byte)
VARIANTS = {
    'binary':  ((ZWSP, ZWNJ), None),
    'ternary': ((ZWSP, ZWNJ, ZWJ), 11),
    'quinary': ((ZWSP, ZWNJ, ZWJ, LRM, RLM), 7),
}
ALIASES = {'': "binary", 2: "binary", 'bin': "binary", 3: "ternary", 'zwsp': "ternary", 5: "quinary", 'full': "quinary"}


def __variant(variant):
    return VARIANTS[ALIASES.get(variant, variant)]


def zerowidth_encode(variant=""):
    alphabet, width = __variant(variant)
    def encode(text, errors="strict"):
        text, r = ensure_str(text), []
        if width is None:
            r = [alphabet[int(b)] for b in "".join(f"{c:08b}" for c in text.encode("utf-8"))]
        else:
            _h, n = handle_error("zero-width", errors), len(alphabet)
            for i, c in enumerate(text):
                if (o := ord(c)) >= n ** width:
                    r.append(_h(c, i))
                    continue
                digits = []
                for _ in range(width):
                    o, d = divmod(o, n)
                    digits.append(alphabet[d])
                r.extend(digits[::-1])
        return (s := "".join(r)), len(s)
    return encode


def zerowidth_decode(variant=""):
    alphabet, width = __variant(variant)
    def decode(text, errors="strict"):
        _h = handle_error("zero-width", errors, decode=True)
        # characters out of the alphabet belong to the cover text, hence they are ignored
        digits = [alphabet.index(c) for c in ensure_str(text) if c in alphabet]
        r, n, size = "", len(alphabet), width or 8
        if (l := len(digits) - len(digits) % size) != len(digits):
            # incomplete trailing character ; decode what precedes, then handle the remainder as an error
            r = decode("".join(alphabet[d] for d in digits[:l]), errors)[0]
            return (s := r + _h("".join(map(str, digits[l:])), l, r)), len(s)
        values = [sum(d * n ** (size - 1 - k) for k, d in enumerate(digits[i:i+size])) for i in range(0, l, size)]
        if width is None:
            data, i = bytes(values), 0
            while i < len(data):
                try:
                    r += data[i:].decode("utf-8")
                    break
                except UnicodeDecodeError as e:
                    r += data[i:i+e.start].decode("utf-8")
                    r += _h(f"\\x{data[i+e.start]:02x}", (i + e.start) * 8, r)
                    i += e.start + 1
        else:
            r = "".join(map(chr, values))
        return r, len(r)
    return decode


add("zero-width", zerowidth_encode, zerowidth_decode,
    r"^zero[-_]?width(?:[-_](2|3|5|bin(?:ary)?|ternary|quinary|zwsp|full))?$",
    expansion_factor=lambda f, e: (11., .05) if e.endswith(("3", "ternary", "zwsp")) else \
                                  (7., .05) if e.endswith(("5", "quinary", "full")) else (8., .05))
