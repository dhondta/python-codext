# -*- coding: UTF-8 -*-
"""Whitespace Codec - whitespace/tabs content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
import random
import re
from string import printable

from ..__common__ import *


__examples1__ = {
    'enc(whitespace|whitespaces)':             {'test': "\t   \t \t\t\t  \t\t \t \t   \t\t  \t   \t \t\t"},
    'enc(whitespace-inv|whitespace_inverted)': {'test': " \t\t\t \t   \t\t  \t \t \t\t\t  \t\t \t\t\t \t  "},
}
__guess1__ = ["whitespace", "whitespace-inv"]
__guess2__ = ["whitespace+after-before", "whitespace-after+before"]


ENCMAP = {r'': {'0': "\t", '1': " "}, r'[-_]inv(erted)?': {'0': " ", '1': "\t"}}
add_map("whitespace", ENCMAP, intype="bin", pattern=r"^whitespaces?([-_]inv(?:erted)?)?$", examples=__examples1__,
        guess=__guess1__, entropy=1., printables_rate=1., expansion_factor=8.)


def wsba_encode(p):
    eq = "ord(c)" + p
    def encode(text, errors="strict"):
        r = []
        for i, c in enumerate(text):
            if ord(c) < min(ord(c) for c in printable[:-6]):
                r.append(handle_error("whitespace" + p, errors, repl_char="\x00")(c, i))
                continue
            enc = "\x00"
            offset = random.randint(-10,10)
            while enc not in printable[:-6]:
                after = random.randint(0, 20)
                before = random.randint(0, 20)
                enc = chr(eval(eq) % 256)
            r.append(" " * before + enc + " " * after)
        s = "\n".join(r)
        return s, len(s)
    return encode


def wsba_decode(p):
    eq = "ord(c)" + "".join({'-':"+",'+':"-"}.get(c, c) for c in p)
    def decode(text, errors="strict"):
        s = ""
        for i, l in enumerate(text.split("\n")):
            ll = len(l.strip())
            if ll == 0:
                continue
            if ll > 1:
                s += handle_error("whitespace_after_before", errors, decode=True, item="line")(l, i)
            after = len(l) - len(l.rstrip(" "))
            before = len(l) - len(l.lstrip(" "))
            c = l[before]
            s += chr(eval(eq))
        return s, len(text)
    return decode


op = r"[+-](?:\d+(?:\.\d+)?[*/])?"
add("whitespace_after_before", wsba_encode, wsba_decode, guess=__guess2__, entropy=1., printables_rate=1., penalty=.1,
    expansion_factor=(22., 3.), pattern=r"whitespace("+op+r"before"+op+r"after|"+op+r"after"+op+r"before)$")

