# -*- coding: UTF-8 -*-
"""ARABICA-2RS Codec - ARABICA-2RS content encoding.

ARABICA-2RS is a toy encoding found on online JavaScript encryption tools. The text is encoded like JavaScript's
 encodeURIComponent() does, then each of its characters (written as 5 digits in base 3 by the original JavaScript) is
 substituted by an Arabic letter (or a similar character), the encoded text ending with "ش". The original JavaScript
 reverses the text before and after the substitution (which cancel each other) and inserts random spaces, which are
 ignored when decoding ; this codec gives an encoded text without spaces, and encodes a text holding "ش" (that the
 original JavaScript leaves as is). When decoding, the left-to-right marks around "ݣ" (easily lost) are optional.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://github.com/gungunfebrianza/Mastering-Cryptography/blob/master/ARABICA2RS/arabperkasaahaha.js
"""
import re

from ._jsuri import substitution
from ..__common__ import *


__examples__ = {
    'enc(arabica-2rs|arabica2rs|arabica_2rs)': {
        'test': '\u062d\u0628\u0637\u062d\u0634',
        'Hello, World!':
            '\u06f1\u0628\u0639\u0639\u0645\ufebf\u0623\u06cc\ufebf\u0623\ufeb9\ufe9b\u0645\u064a\u0639\u062e\ufb90'
            '\u0634',
        '5': '\u200e\u0763\u200e\u0634',
        '': '',
    },
    'dec(arabica-2rs)': {
        '\u062d\u0628\u0637\u062d\u0634': 'test',
        '\u06f1\u0628 \u0639 \u0639\u0645 \ufebf\u0623 \u06cc\ufebf\u0623 \ufeb9 \ufe9b\u0645\u064a\u0639\u062e\ufb90'
        '\u0634':
            'Hello, World!',
        '\u0763\u0634': '5',
        '\u062d\u0628X\u0634': None,
        '\ufebf\u0634': None,
    },
    'enc-dec(arabica-2rs)': ['', 'test', 'Hello, World!', 'caf\xe9 \u20ac \U0001f600 \u0634', "0123456789-_.!~*'()%"],
}
__guess__ = ["arabica-2rs"]


# substitutes of the characters of the URI-encoded text, given by their codes in base 3 (as in the original JavaScript)
ARABICA = [
    ("10121", "غ"), ("10122", "ظ"), ("10200", "ذ"), ("10201", "خ"), ("10202", "ب"), ("10210", "ت"),
    ("10211", "س"), ("10212", "ر"), ("10220", "ق"), ("10221", "ض"), ("10222", "ف"), ("11000", "ع"),
    ("11001", "ص"), ("11002", "ن"), ("11010", "م"), ("11011", "ل"), ("11012", "ك"), ("11020", "ي"),
    ("11021", "ط"), ("11022", "ح"), ("11100", "ز"), ("11101", "و"), ("11102", "ه"), ("11110", "د"),
    ("11111", "ج"), ("11112", "ﺵ"), ("01210", "ﺹ"), ("01211", "ﻃ"), ("01212", "أ"), ("01220", "ا"),
    ("01221", "ـ"), ("01222", "\u200eݣ\u200e"), ("02000", "چ"), ("02001", "گ"), ("02002", "آ"), ("02010", "ة"),
    ("02102", "ى"), ("02110", "ک"), ("02111", "ی"), ("02112", "پ"), ("02120", "۴"), ("02121", "۸"),
    ("02122", "۶"), ("02200", "۱"), ("02201", "ﭻ"), ("02202", "ئ"), ("02210", "ە"), ("02211", "ﻼ"),
    ("02212", "ﻻ"), ("02220", "\u0651"), ("02221", "\u0650"), ("02222", "ژ"), ("10000", "ڨ"), ("10001", "ڜ"),
    ("10002", "ﷲ"), ("10010", "ﺑ"), ("10011", "ﭘ"), ("10012", "ﺗ"), ("10020", "ﺛ"), ("10021", "ﺟ"),
    ("10022", "ﺣ"), ("10100", "ﺡ"), ("01101", "ﺿ"), ("01111", "ﻏ"), ("01112", "ﻓ"), ("01200", "ﻑ"),
    ("01120", "ﻕ"), ("01020", "ﮐ"), ("10112", "ﻝ"), ("01201", "ﻡ"), ("01110", "ﻥ"), ("11200", "ﻳ"),
]
_TABLE = {chr(int(code, 3)): s for code, s in ARABICA}
_encode, _decode = substitution("arabica-2rs", _TABLE, {s.strip("\u200e"): c for c, s in _TABLE.items()})


def arabica_encode(text, errors="strict"):
    t = ensure_str(text)
    return "".join(_encode(t)) + "\u0634" if t else "", len(text)


def arabica_decode(text, errors="strict"):
    t = re.sub(r"[\s\u200e]+", "", ensure_str(text)).replace("\u0634", "")
    return _decode(t, errors), len(text)


add("arabica-2rs", arabica_encode, arabica_decode, r"^arabica[-_]?2rs$", examples=__examples__, guess=__guess__)
