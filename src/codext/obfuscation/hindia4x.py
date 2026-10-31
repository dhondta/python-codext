# -*- coding: UTF-8 -*-
"""HINDIA-4X Codec - HINDIA-4X content encoding.

HINDIA-4X is a toy encoding found on online JavaScript encryption tools. The pairs of letters "oo", "ii", "ee", "tt" and
 "rr" of the text are first replaced by "ṍ", "¡", "ə", "ṯ" and "ṝ", then the text is encoded like JavaScript's
 encodeURIComponent() does, and its characters, in reverse order, are each substituted (from their codes, written as 5
 digits in base 3 by the original JavaScript) by a Bengali or Devanagari character (or "অ।"), a space being inserted
 every 4 characters and the encoded text ending with "ভ". Decoding gives back these pairs of letters, hence a text
 holding one of these 5 characters is not decoded as it was. As with the original JavaScript, the spaces are ignored
 when decoding ; unlike it, this codec encodes a text holding "ভ" (that the original JavaScript leaves as is).

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://web.archive.org/web/20121203064815/http://crypo.in.ua/tools/eng_hindia-4x.php
"""
import re

from ._jsuri import substitution
from ..__common__ import *


__examples__ = {
    'enc(hindia-4x|hindia4x|hindia_4x)': {
        'test': 'ছএकছভ',
        'Hello, World!':
            'ाযনণ ্सउच वৎचव ্ননक '
            'दভ',
        '5': 'অ।ভ',
        '': '',
    },
    'dec(hindia-4x)': {
        'ছএकছভ': 'test',
        'ाযনণ্सउ चवৎचव্ন নकदভ':
            'Hello, World!',
        'অ ।ভ': '5',
        'ছXভ': None,
        'वভ': None,
    },
    'enc-dec(hindia-4x)': ['', 'test', 'Hello, World!', 'caf\xe9 € \U0001f600 ভ', 'boot keeper tt rr ii',
                           "0123456789-_.!~*'()%"],
}
__guess__ = ["hindia-4x"]


# pairs of letters replaced before encoding, in this order
DIGRAPHS = [("oo", "ṍ"), ("ii", "¡"), ("ee", "ə"), ("tt", "ṯ"), ("rr", "ṝ")]
# substitutes of the characters of the URI-encoded text, given by their codes in base 3 (as in the original JavaScript)
HINDIA = [
    ("10121", "फ"), ("10122", "ৰ"), ("10200", "ত"), ("10201", "য"), ("10202", "क"), ("10210", "দ"), ("10211", "ड"),
    ("10212", "শ"), ("10220", "চ"), ("10221", "ক"), ("10222", '\u09c0'), ("11000", "ন"), ("11001", "ম"), ("11002", "ल"),
    ("11010", '\u09cd'), ("11011", "জ"), ("11012", "ষ"), ("11020", "ণ"), ("11021", "এ"), ("11022", "ছ"), ("11100", "ধ"),
    ("11101", "ৱ"), ("11102", "স"), ("11110", "থ"), ("11111", "খ"), ("11112", "ট"), ("01210", "उ"), ("01211", "গ"),
    ("01212", "च"), ("01220", "ল"), ("01221", "আ"), ("01222", "অ।"), ("02000", "ফ"), ("02001", "প"), ("02002", "ई"),
    ("02010", "ব"), ("02102", "হ"), ("02110", '\u0982'), ("02111", "ৎ"), ("02112", "ह"), ("02120", '\u093f'),
    ("02121", "न"), ("02122", "ग"), ("02200", "द"), ("02201", '\u0940'), ("02202", '\u09c1'), ("02210", "आ"),
    ("02211", "ঙ"), ("02212", "উ"), ("02220", "ঠ"), ("02221", "प"), ("02222", "ঘ"), ("10000", "৭"), ("10001", "৫"),
    ("10002", "১"), ("10010", "त"), ("10011", "৬"), ("10012", "ই"), ("10020", "स"), ("10021", "य"), ("10022", "म"),
    ("10100", '\u0947'), ("01101", "व"), ("01111", "ज"), ("01112", "র"), ("01200", "ড"), ("01120", "भ"),
    ("01020", '\u093e'), ("10112", "र"), ("01201", "छ"), ("01110", "अ"), ("11200", '\u0941'),
]
_encode, _decode = substitution("hindia-4x", {chr(int(code, 3)): s for code, s in HINDIA})


def hindia_encode(text, errors="strict"):
    t = ensure_str(text)
    if t == "":
        return "", len(text)
    for pair, c in DIGRAPHS:
        t = t.replace(pair, c)
    r = "".join(reversed(_encode(t)))
    return " ".join(r[i:i+4] for i in range(0, len(r), 4)) + "ভ", len(text)


def hindia_decode(text, errors="strict"):
    t = re.sub(r"\s+", "", ensure_str(text)).replace("ভ", "")
    r = _decode(reversed(re.findall(r"অ।|.", t, re.S)), errors)
    for pair, c in DIGRAPHS:
        r = r.replace(c, pair)
    return r, len(text)


add("hindia-4x", hindia_encode, hindia_decode, r"^hindia[-_]?4x$", examples=__examples__, guess=__guess__)
