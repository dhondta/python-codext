# -*- coding: UTF-8 -*-
"""Whitespace Codec - whitespace/tabs content encoding.

These codecs hide a text in whitespace characters:

- "whitespace": each bit of the characters is written as a tab (0) or a space (1), or the opposite with "-inv", hence an
   invisible text
- "whitespace+after-before" (or another arithmetic expression of "after" and "before"): each character is written on its
   own line as a printable character surrounded by random numbers of spaces before and after it, the original character
   being the printable one shifted according to the expression of these numbers

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
    'enc(whitespace+after-before)':     {'Test\r': None, 'Test\xff': None, 'Test\u0141': None},
    'enc-dec(whitespace+after-before)': ["Test", "TESTSTRING!"],
}
__guess1__ = ["whitespace", "whitespace-inv"]
__guess2__ = ["whitespace+after-before", "whitespace-after+before"]


ENCMAP = {r'': {'0': "\t", '1': " "}, r'[-_]inv(erted)?': {'0': " ", '1': "\t"}}
add_map("whitespace", ENCMAP, intype="bin", pattern=r"^whitespaces?([-_]inv(?:erted)?)?$", examples=__examples1__,
        guess=__guess1__, entropy=1., printables_rate=1., expansion_factor=8.)


PRINTABLES = printable[:-6]
PRINTABLE_ORDS = set(map(ord, PRINTABLES))


def wsba_encode(p):
    # the expression comes from the codec name, validated by its pattern
    f = eval("lambda o, after, before: o" + p)
    
    def _value(o, after, before):
        try:
            return f(o, after, before)
        except ZeroDivisionError:
            return
    
    def _pairs(c):
        """ Get the numbers of spaces (after, before) that shift the given character to a printable one that decodes
             back to it ; there is none for characters lower than the first printable or too far from the printables. """
        if ord(c) < min(PRINTABLE_ORDS):
            return []
        return [(a, b) for a in range(21) for b in range(21)
                if isinstance(v := _value(ord(c), a, b), int) and v in PRINTABLE_ORDS]
    
    def encode(text, errors="strict"):
        r, _h, pairs = [], handle_error("whitespace_after_before", errors, repl_char="\x00"), {}
        for i, c in enumerate(text):
            if c not in pairs:
                pairs[c] = _pairs(c)
            if len(pairs[c]) == 0:
                r.append(_h(c, i))
            else:
                # choosing among the valid pairs is equivalent to drawing random pairs until the result is printable
                after, before = random.choice(pairs[c])
                r.append(" " * before + chr(f(ord(c), after, before)) + " " * after)
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
                continue
            after, before = len(l) - len(l.rstrip(" ")), len(l) - len(l.lstrip(" "))
            c = l[before]
            s += chr(eval(eq))
        return s, len(s)
    return decode


op = r"[+-](?:\d+(?:\.\d+)?[*/])?"
add("whitespace_after_before", wsba_encode, wsba_decode, examples=__examples2__, guess=__guess2__,
    printables_rate=1., penalty=.1, expansion_factor=(22., 3.), entropy=1.,
    pattern=r"whitespace("+op+r"before"+op+r"after|"+op+r"after"+op+r"before)$")

