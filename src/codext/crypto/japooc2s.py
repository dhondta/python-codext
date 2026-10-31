# -*- coding: UTF-8 -*-
"""JAPOO-C2S Codec - JAPOO-C2S content encryption.

JAPOO-C2S is a toy cipher found on online JavaScript encryption tools. The text is encoded like JavaScript's
 encodeURIComponent() does, then each of its characters (written as 6 digits in base 3 by the original JavaScript) is
 substituted by a Chinese or Japanese character followed by a space, some pairs of identical characters (e.g. "貴 貴 ")
 being then replaced by another character (e.g. "詞 "), and the ciphertext ends with "类". As with the original
 JavaScript, the spaces are ignored when decoding ; unlike it, this codec encodes a text holding "类" (that the original
 JavaScript leaves as is).

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://www.persona-shield.com/japoo-c2s.htm
"""
import re

from ._jsuri import substitution
from ..__common__ import *


__examples__ = {
    'enc(japoo-c2s|japooc2s|japoo_c2s)': {
        'test': '\u5f92 \u6216 \u7c21 \u5f92 \u7c7b',
        'too': '\u5f92 \u578b \u7c7b',
        '000': '\u8a5e \u8cb4 \u7c7b',
        '': '',
    },
    'dec(japoo-c2s)': {
        '\u5f92 \u6216 \u7c21 \u5f92 \u7c7b': 'test',
        '\u5f92\u578b\u7c7b': 'too',
        '\u5f92X\u7c7b': None,
        '\u5834 \u7c7b': None,
    },
    'enc-dec(japoo-c2s)': ['', 'test', 'Hello, World!', 'caf\xe9 \u20ac \U0001f600 \u7c7b', '0000 too ooo'],
}
__guess__ = ["japoo-c2s"]


# substitutes of the characters of the URI-encoded text, given by their codes in base 3 (as in the original JavaScript)
JAPOO = [
    ("002120", "僕"), ("001101", "場"), ("001212", "誰"), ("011020", "歌"), ("001210", "貴"), ("011010", "前"),
    ("001020", "積"), ("011002", "書"), ("010202", "或"), ("011022", "徒"), ("010212", "卵"), ("011110", "面"),
    ("010200", "本"), ("010220", "語"), ("010201", "音"), ("010122", "ほ"), ("011021", "簡"), ("001201", "息"),
    ("002220", "信"), ("001220", "稱"), ("011101", "语"), ("011111", "文"), ("010121", "是"), ("011011", "種"),
    ("010010", "主"), ("011001", "要"), ("011100", "為"), ("002112", "列"), ("002102", "島"), ("010022", "和"),
    ("001211", "民"), ("001221", "族"), ("010210", "所"), ("010211", "使"), ("010221", "用"), ("010222", "的"),
    ("011000", "也"), ("011112", "有"), ("011012", "學"), ("011102", "者"), ("001222", "認"), ("002000", "孤"),
    ("002002", "立"), ("002010", "徵"), ("002121", "其"), ("002122", "寫"), ("002200", "系"), ("002201", "統"),
    ("002202", "包"), ("002210", "括"), ("002211", "多"), ("002110", "數"), ("002111", "漢"), ("002212", "字"),
    ("002221", "又"), ("002222", "及"), ("010000", "訓"), ("010001", "讀"), ("010002", "等"), ("010011", "參"),
    ("010012", "考"), ("010020", "分"), ("010021", "布"), ("010100", "節"), ("002001", "域"), ("001111", "排"),
    ("001112", "官"), ("001200", "言"), ("001120", "會"), ("011200", "碼"), ("010112", "科"), ("001110", "實"),
]
# characters replacing pairs of identical characters, in this order
PAIRS = [
    ("貴", "詞"), ("民", "單"), ("誰", "如"), ("稱", "彼"), ("族", "他"), ("認", "叫"), ("孤", "共"),
    ("域", "関"), ("立", "弁"), ("徵", "降"), ("前", "型"), ("語", "類"), ("或", "賓"),
]
_encode, _decode = substitution("japoo-c2s", {chr(int(code, 3)): s for code, s in JAPOO})


def japoo_encode(text, errors="strict"):
    t = ensure_str(text)
    if t == "":
        return "", len(text)
    r = "".join(s + " " for s in _encode(t))
    for c, pair in PAIRS:
        r = r.replace(f"{c} {c} ", f"{pair} ")
    return r + "\u7c7b", len(text)


def japoo_decode(text, errors="strict"):
    t = re.sub(r"\s+", "", ensure_str(text)).replace("\u7c7b", "")
    for c, pair in PAIRS:
        t = t.replace(pair, c + c)
    return _decode(t, errors), len(text)


add("japoo-c2s", japoo_encode, japoo_decode, r"^japoo[-_]?c2s$", examples=__examples__, guess=__guess__)
