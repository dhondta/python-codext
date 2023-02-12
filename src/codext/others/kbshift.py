# -*- coding: UTF-8 -*-
"""Keyboard-Shift Codec - keyboard line shifting content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


LAYOUTS = {
    'ansi':      "~!@#$%^&*()_+\n`1234567890-=\nqwertyuiop{}|\n[]\\\nasdfghjkl:\"\n;'\nzxcvbnm<>\n,./",
    'azerty':    "azertyuiop\nqsdfghjklm\nwxcvbn",
    'azerty-be': "³1234567890°_\n²&é\"'(§è!çà)-\n|@#^{}\nazertyuiop$\n€[]\n¨*\nqsdfghjklm%£\nùµ\n´`\n>wxcvbn?./+\n<,;:=\n\\~",
    'azerty-fr': "1234567890°+\n²&é\"'(-è_çà)=\n~#{[|`\\^@]}\nazertyuiop¨£\nqsdfghjklm%µ\nù*\n>wxcvbn?./§\n<,;:!",
    'dvorak':    "~!@#$%^&*(){}\n`1234567890[]\n\"<>pyfgcrl?+|\n',./=\\\naoeuidhtns_\n-\n:qjkxbmwvz\n;",
    'qwerty':    "qwertyuiop\nasdfghjkl\nzxcvbnm",
    'qwerty-us': "~!@#$%^&*()_+\n`1234567890-=\nqwertyuiop{}|\n[]\\\nasdfghjkl:\"\n;,\nzxcvbnm<>?\n./",
}
__per_len = {}
for k, s in LAYOUTS.items():
    i = max(map(len, s.split("\n")))
    __per_len.setdefault(i, [])
    __per_len[i].append(k)


__examples__ = {"enc-dec(kbshift_%s_%d)" % (kb, n): ["@irandom{256,512}"] for n in range(10) for kb in LAYOUTS.keys()}
__guess__ = []
for mlen, kbs in __per_len.items():
    for k in kbs:
        __guess__.extend(["kbshift-%s-%d" % (k, i+1) for i in range(mlen)])


def _kbshift(text, keyboard="azerty", n=1, decode=False):
    r = ""
    for c in text:
        nc = None
        for l in LAYOUTS[keyboard].splitlines():
            if c.lower() in l:
                nc = l[(l.index(c.lower()) + [-1, 1][decode] * n) % len(l)]
                break
        r += c if nc is None else nc
    return r


def kbshift_encode(scheme):
    kb, shift = re.match(r"^(.*?)[-_]?(\d+)$", scheme or "azerty-1").groups()
    def encode(text, errors="strict"):
        r = _kbshift(ensure_str(text), kb, int(shift))
        return r, len(r)
    return encode


def kbshift_decode(scheme):
    kb, shift = re.match(r"^(.*?)[-_]?(\d+)$", scheme or "azerty-1").groups()
    def decode(text, errors="strict"):
        r = _kbshift(ensure_str(text), kb, int(shift), True)
        return r, len(r)
    return decode


add("kbshift", kbshift_encode, kbshift_decode, entropy=lambda e: e,printables_rate=lambda pr: pr, transitive=True,
    pattern=r"^kbshift(?:|[-_]((?:az|qw)erty[-_]?[1-9]|(?:ansi|azerty-(?:be|fr)|dvorak|qwerty-us)[-_]?(?:[1-9]|1[0-2])))$")

