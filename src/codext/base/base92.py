# -*- coding: UTF-8 -*-
"""Base92 Codec - base92 content encoding.

Base92, designed by Nathan Hwang (thenoviceoof), uses 91 printable ASCII characters ("!", then "#" to "_" and "a" to
 "}", hence all but space, '"', "`" and "~"), the empty string being encoded as "~". The input bits are read by groups
 of 13 bits, each group being written with 2 characters (91 x 91 = 8281 >= 8192), hence an expansion of about 23% ; the
 last bits are padded with zeros and written with a single character if they fit in 6 bits, or with 2 characters
 otherwise. When decoding, a pair of characters whose value exceeds 13 bits is invalid, as well as a single character.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://github.com/thenoviceoof/base92
"""
from ._base import main
from ..__common__ import *


__examples__ = {
    'enc(base92|base-92|base_92)': {'hello world': "Fc_$aOTdKnsM*k", '': "~", 'a': "D,",
                                    '^\xb6;\xbb\xe0\x1e\xee\xd0\x93\xcb"\xbb\x8fZ\xcd\xc3': "C=i.w6'IvB/viUpRAwco"},
    'dec(base92)': {'Fc_$aOTdKnsM*k': "hello world", '~': "", 'Fc_$aOTd\nKnsM*k': "hello world", 'F': None,
                    'Fc"$': None, '}}': None, 'Fc~': None},
    'enc-dec(base92)': ["test", "This is a test", "aoeuaoeuaoeu", "@random{512,1024,2048}"],
}
__guess__ = ["base92"]


_range = lambda c1, c2: "".join(chr(c) for c in range(ord(c1), ord(c2) + 1))
B92 = "!" + _range("#", "_") + _range("a", "}")
B92_VALUES = {c: i for i, c in enumerate(B92)}


def base92_encode(text, errors="strict"):
    t = b(text)
    if len(t) == 0:
        return "~", 0
    r, bits, n = [], 0, 0
    for byte in t:
        bits, n = (bits << 8) | byte, n + 8
        while n >= 13:
            n -= 13
            v, bits = bits >> n, bits & ((1 << n) - 1)
            r.extend((B92[v // 91], B92[v % 91]))
    # the last bits are padded with zeros, to 6 bits (1 character) or to 13 bits (2 characters)
    if n > 0:
        if n < 7:
            r.append(B92[bits << (6 - n)])
        else:
            v = bits << (13 - n)
            r.extend((B92[v // 91], B92[v % 91]))
    return "".join(r), len(t)


def base92_decode(text, errors="strict"):
    t = ensure_str(_stripl(text, True, True))
    if t == "~":
        return "", len(text)
    _h = handle_error("base92", errors, decode=True)
    # characters out of the alphabet are errors (only skipped if errors are not handled strictly)
    values, r = [], bytearray()
    for i, c in enumerate(t):
        if c in B92_VALUES:
            values.append(B92_VALUES[c])
        else:
            _h(c, i, bytes(r))
    if len(values) == 1:
        _h(t, 0, bytes(r))
        return "", len(text)
    bits, n = 0, 0
    for i in range(0, len(values) - 1, 2):
        v = values[i] * 91 + values[i+1]
        if v >= 8192:
            _h(t[i:i+2], i, bytes(r))
            continue
        bits, n = (bits << 13) | v, n + 13
        while n >= 8:
            n -= 8
            r.append(bits >> n)
            bits &= (1 << n) - 1
    # a single last character holds 6 bits ; the padding bits that remain are dropped
    if len(values) % 2 == 1:
        bits, n = (bits << 6) | values[-1], n + 6
        while n >= 8:
            n -= 8
            r.append(bits >> n)
            bits &= (1 << n) - 1
    return bytes(r), len(text)


add("base92", base92_encode, base92_decode, r"^base[-_]?92$", entropy=6.5, expansion_factor=1.231, len_charset=91,
    printables_rate=1.)
main92 = main(92, "<https://github.com/thenoviceoof/base92>", inv=False)
