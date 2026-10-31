# -*- coding: UTF-8 -*-
"""ATOM-128 Codec - ATOM-128 content encoding.

ATOM-128 is a toy encoding found on online JavaScript encryption tools. It is Base64 with a shuffled alphabet, whose
 65th character ("C") is used for padding. As in the original JavaScript, the text is first escaped with JavaScript's
 escape() (e.g. " " becoming "%20" and "é" becoming "%E9"), and unescaped after decoding ; encoded texts made without
 this escaping (i.e. from the UTF-8 bytes of the text) are then decoded the same way.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://github.com/gungunfebrianza/Mastering-Cryptography/blob/master/ATOM-128/ATOM-128.js
"""
from ._jsbase64 import js_base64
from ..__common__ import add


__examples__ = {
    'enc(atom128|atom-128|atom_128)': {'this is a test': "0IXBnsgsSI6tQfPqKDgsSoA6nmbC", 'test': "0IHt0/CC", '': ""},
    'dec(atom128)': {'0IHt0/CC': "test", '0IHt 0/CC': "test", '0IHt0/C': None, '0IHt0/C%': None},
    'enc-dec(atom128)': ["this is a test", "Hello, World! 1234", "\xe9t\xe9 \u2603 \U0001F600", "100% sure", "a"],
}
__guess__ = ["atom128"]


add("atom128", *js_base64("atom128", "/128GhIoPQROSTeUbADfgHijKLM+n0pFWXY456xyzB7=39VaqrstJklmNuZvwcdEC"),
    r"^atom[-_]?128$", printables_rate=1., expansion_factor=(1.6, .3))
