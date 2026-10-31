# -*- coding: UTF-8 -*-
"""CHINZO-72C Codec - CHINZO-72C content encoding.

CHINZO-72C is a toy encoding found on online JavaScript encryption tools. The pairs of letters "oo", "ii", "ee", "tt"
 and "rr" of the text are first replaced by Chinese characters ("讲", "邻", "头", "会" and "歷"), then the text is encoded
 like JavaScript's encodeURIComponent() does, and each of its characters (written as 4 digits in base 4 by the original
 JavaScript) is substituted by a Chinese character followed by a space, the encoded text ending with "吴". Decoding gives
 back these pairs of letters, hence a text holding one of these 5 Chinese characters is not decoded as it was. As with
 the original JavaScript, the spaces are ignored when decoding ; unlike it, this codec encodes a text holding "吴" (that
 the original JavaScript leaves as is).

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://github.com/gungunfebrianza/Mastering-Cryptography/blob/master/CHINZO-72C/chinzo72c.js
"""
import re

from ._jsuri import substitution
from ..__common__ import *


__examples__ = {
    'enc(chinzo-72c|chinzo72c|chinzo_72c)': {
        'test': '\u5c9b \u4f10 \u592b \u5c9b \u5434',
        'too': '\u5c9b \u9898 \u9020 \u7b87 \u9898 \u5462 \u9020 \u9898 \u547d \u9632 \u5434',
        '': '',
    },
    'dec(chinzo-72c)': {
        '\u5c9b \u4f10 \u592b \u5c9b \u5434': 'test',
        '\u5c9b\u4f10\u592b\u5c9b\u5434': 'test',
        '\u5c9bX\u5434': None,
        '\u9898 \u5434': None,
    },
    'enc-dec(chinzo-72c)': ['', 'test', 'Hello, World!', 'caf\xe9 \u20ac \U0001f600 \u5434', 'boot keeper tt rr ii'],
}
__guess__ = ["chinzo-72c"]


# pairs of letters replaced before encoding, in this order
DIGRAPHS = [("oo", "讲"), ("ii", "邻"), ("ee", "头"), ("tt", "会"), ("rr", "歷")]
# substitutes of the characters of the URI-encoded text, given by their codes in base 4 (as in the original JavaScript)
CHINZO = [
    ("1201", "法"), ("1202", "弗"), ("1203", "朗"), ("1210", "斯"), ("1211", "伐"), ("1212", "世"), ("1213", "来"),
    ("1220", "拉"), ("1221", "玛"), ("1222", "里"), ("1223", "娘"), ("1230", "战"), ("1231", "争"), ("1232", "径"),
    ("1233", "打"), ("1300", "到"), ("1301", "赛"), ("1302", "依"), ("1303", "夫"), ("1310", "岛"), ("1311", "看"),
    ("1312", "渠"), ("1313", "析"), ("1320", "马"), ("1321", "根"), ("1322", "就"), ("0300", "呒"), ("0301", "没"),
    ("0302", "防"), ("0303", "止"), ("0310", "侵"), ("0311", "略"), ("0312", "设"), ("0313", "施"), ("0320", "箇"),
    ("0321", "咾"), ("1001", "呢"), ("1002", "命"), ("1003", "令"), ("1010", "浪"), ("1011", "造"), ("1012", "座"),
    ("1013", "城"), ("1020", "隔"), ("1021", "脱"), ("1022", "年"), ("1023", "西"), ("1030", "班"), ("1031", "国"),
    ("1032", "洛"), ("1033", "收"), ("1100", "神"), ("1101", "圣"), ("1102", "罗"), ("1103", "帝"), ("1110", "例"),
    ("1111", "想"), ("1112", "拿"), ("1113", "吃"), ("1120", "落"), ("1121", "然"), ("1122", "特"), ("0211", "题"),
    ("0220", "进"), ("0221", "要"), ("0222", "强"), ("0231", "也"), ("1332", "是"), ("0201", "始"), ("1133", "建"),
    ("0232", "望"), ("0213", "保"),
]
_encode, _decode = substitution("chinzo-72c", {chr(int(code, 4)): s for code, s in CHINZO})


def chinzo_encode(text, errors="strict"):
    t = ensure_str(text)
    if t == "":
        return "", len(text)
    for pair, c in DIGRAPHS:
        t = t.replace(pair, c)
    return "".join(s + " " for s in _encode(t)) + "\u5434", len(text)


def chinzo_decode(text, errors="strict"):
    r = _decode(re.sub(r"\s+", "", ensure_str(text)).replace("\u5434", ""), errors)
    for pair, c in DIGRAPHS:
        r = r.replace(c, pair)
    return r, len(text)


add("chinzo-72c", chinzo_encode, chinzo_decode, r"^chinzo[-_]?72c$", examples=__examples__, guess=__guess__)
