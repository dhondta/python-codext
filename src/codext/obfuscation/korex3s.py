# -*- coding: UTF-8 -*-
"""KOREX-3S Codec - KOREX-3S content encoding.

KOREX-3S is a toy encoding found on online JavaScript encryption tools. The text is encoded like JavaScript's
 encodeURIComponent() does, then its characters, in reverse order, are each substituted (from their codes, written as 5
 digits in base 3 by the original JavaScript) by a Korean Hangul syllable (or a Chinese character) followed by a space,
 the encoded text ending with "한". As with the original JavaScript, the spaces are ignored when decoding ; unlike it,
 this codec encodes a text holding "한" (that the original JavaScript leaves as is).

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://web.archive.org/web/20121203064839/http://crypo.in.ua/tools/eng_korex-3s.php
"""
import re

from ._jsuri import substitution
from ..__common__ import *


__examples__ = {
    'enc(korex-3s|korex3s|korex_3s)': {
        'test': '지 등 대 지 한',
        'Hello, World!': '경 서 화 롯 위 키 고 이 南 도 이 南 위 화 '
                         '화 대 표 한',
        '5': '명 한',
        '': '',
    },
    'dec(korex-3s)': {
        '지 등 대 지 한': 'test',
        '지등대지한': 'test',
        '지X한': None,
        '南 한': None,
    },
    'enc-dec(korex-3s)': ['', 'test', 'Hello, World!', 'caf\xe9 € \U0001f600 한', "0123456789-_.!~*'()%"],
}
__guess__ = ["korex-3s"]


# substitutes of the characters of the URI-encoded text, given by their codes in base 3 (as in the original JavaScript)
KOREX = [
    ("10121", "국"), ("10122", "는"), ("10200", "에"), ("10201", "서"), ("10202", "대"), ("10210", "민"), ("10211", "조"),
    ("10212", "선"), ("10220", "주"), ("10221", "의"), ("10222", "공"), ("11000", "화"), ("11001", "중"), ("11002", "족"),
    ("11010", "위"), ("11011", "을"), ("11012", "비"), ("11020", "롯"), ("11021", "등"), ("11022", "지"), ("11100", "로"),
    ("11101", "카"), ("11102", "자"), ("11110", "흐"), ("11111", "스"), ("11112", "앙"), ("01210", "고"), ("01211", "려"),
    ("01212", "이"), ("01220", "共"), ("01221", "사"), ("01222", "명"), ("02000", "후"), ("02001", "치"), ("02002", "를"),
    ("02010", "혼"), ("02102", "하"), ("02110", "기"), ("02111", "도"), ("02112", "함"), ("02120", "릴"), ("02121", "문"),
    ("02122", "말"), ("02200", "표"), ("02201", "준"), ("02202", "원"), ("02210", "음"), ("02211", "러"), ("02212", "있"),
    ("02220", "부"), ("02221", "분"), ("02222", "은"), ("10000", "입"), ("10001", "호"), ("10002", "과"), ("10010", "남"),
    ("10011", "트"), ("10012", "베"), ("10020", "키"), ("10021", "백"), ("10022", "우"), ("10100", "월"), ("01101", "南"),
    ("01111", "다"), ("01112", "시"), ("01200", "토"), ("01120", "많"), ("01020", "경"), ("10112", "상"), ("01201", "오"),
    ("01110", "목"), ("11200", "산"),
]
_encode, _decode = substitution("korex-3s", {chr(int(code, 3)): s for code, s in KOREX})


def korex_encode(text, errors="strict"):
    t = ensure_str(text)
    return "".join(s + " " for s in reversed(_encode(t))) + "한" if t else "", len(text)


def korex_decode(text, errors="strict"):
    t = re.sub(r"\s+", "", ensure_str(text)).replace("한", "")
    return _decode(reversed(t), errors), len(text)


add("korex-3s", korex_encode, korex_decode, r"^korex[-_]?3s$", examples=__examples__, guess=__guess__)
