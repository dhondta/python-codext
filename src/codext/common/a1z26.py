# -*- coding: UTF-8 -*-
"""A1Z26 Codec - A1Z26 content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from string import ascii_lowercase as lower

from ..__common__ import *


SEP = "-_/|,;:*"

__examples__ = {
    'enc(a1z26-BAD)': None,
    'dec(a1z26)':     {'1-12-123':       None},
    'enc(a1z26)':     {'test123': None, 'this is a test': "20-8-9-19 9-19 1 20-5-19-20"},
    'enc(a1z26-/)':   {'this is a test': "20/8/9/19 9/19 1 20/5/19/20"},
}
__guess__ = ["a1z26", "a1z26_"] + ["a1z26-" + s for s in SEP[2:]]


def a1z26_encode(sep):
    sep = sep[-1] if len(sep) > 0 else "-"
    def encode(text, errors="strict"):
        words = []
        for word in text.split():
            w = []
            for k, c in enumerate(word):
                try:
                    w.append(str(lower.index(c.lower()) + 1))
                except ValueError:
                    w.append(handle_error("a1z26", errors)(c, k))
            words.append(sep.join(w).strip(sep))
        return " ".join(words), len(text)
    return encode


def a1z26_decode(sep):
    sep = sep[-1] if len(sep) > 0 else "-"
    def decode(text, errors="strict"):
        k, words = 0, []
        for word in text.split():
            w = ""
            for i in word.split(sep):
                k += 1
                try:
                    w += lower[int(i)-1]
                except IndexError:
                    w += handle_error("a1z26", errors, decode=True)(str(i), k)
            words.append(w)
        return " ".join(words), len(text)
    return decode


add("a1z26", a1z26_encode, a1z26_decode, pattern=r"^a1z26(|[-_]|[-_][/|,;:\*])$", printables_rate=1.)

