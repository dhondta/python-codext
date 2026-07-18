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
__examples2__ = {
    'dec(whitespace+after-before)':     {'}         \n      a  \n  .   v  ': None},
    'enc(whitespace+after-before)':     {'Test\r': None},
    'enc-dec(whitespace+after-before)': ["Test", "TESTSTRING!"],
}
__guess1__ = ["whitespace", "whitespace-inv"]
__guess2__ = ["whitespace+after-before", "whitespace-after+before"]


ENCMAP = {r'': {'0': "\t", '1': " "}, r'[-_]inv(erted)?': {'0': " ", '1': "\t"}}
add_map("whitespace", ENCMAP, intype="bin", pattern=r"^whitespaces?([-_]inv(?:erted)?)?$", examples=__examples1__,
        guess=__guess1__, entropy=1., printables_rate=1., expansion_factor=8.)


def wsba_encode(p):
    eq = "ord(c)" + p
    def encode(text, errors="strict"):
        r, _h = [], handle_error("whitespace" + p, errors, repl_char="\x00")
        for i, c in enumerate(text):
            if ord(c) < min(ord(c) for c in printable[:-6]):
                r.append(_h(c, i))
            else:
                enc, offset = "\x00", random.randint(-10,10)
                while enc not in printable[:-6]:
                    after, before = random.randint(0, 20), random.randint(0, 20)
                    enc = chr(eval(eq) % 256)
                r.append(" " * before + enc + " " * after)
        return (s := "\n".join(r)), len(s)
    return encode


def wsba_decode(p):
    eq = "ord(c)" + "".join({'-':"+",'+':"-"}.get(c, c) for c in p)
    def decode(text, errors="strict"):
        s, _h = "", handle_error("whitespace_after_before", errors, decode=True, item="line")
        for i, l in enumerate(text.split("\n")):
            if (ll := len(l.strip())) == 0:
                continue
            if ll > 1:
                s += _h(l, i)
            after, before = len(l) - len(l.rstrip(" ")), len(l) - len(l.lstrip(" "))
            c = l[before]
            s += chr(eval(eq))
        return s, len(s)
    return decode


op = r"[+-](?:\d+(?:\.\d+)?[*/])?"
add("whitespace_after_before", wsba_encode, wsba_decode, examples=__examples2__, guess=__guess2__,
    printables_rate=1., penalty=.1, expansion_factor=(22., 3.), entropy=1.,
    pattern=r"whitespace("+op+r"before"+op+r"after|"+op+r"after"+op+r"before)$")

