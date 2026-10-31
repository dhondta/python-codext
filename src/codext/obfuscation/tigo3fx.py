# -*- coding: UTF-8 -*-
"""TIGO-3FX Codec - TIGO-3FX content encoding.

TIGO-3FX is a toy encoding found on online JavaScript encryption tools. It is Base64 with a shuffled alphabet, whose
 65th character ("X") is used for padding. As in the original JavaScript, the text is first escaped with JavaScript's
 escape() (e.g. " " becoming "%20" and "é" becoming "%E9"), and unescaped after decoding ; encoded texts made without
 this escaping (i.e. from the UTF-8 bytes of the text) are decoded as well, except that an ASCII text holding escape
 sequences (e.g. "%41") is then unescaped.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: http://qbarbe.free.fr/crypto/eng_tigo3fxe.php
"""
from ._jsbase64 import js_base64
from ..__common__ import add


__examples__ = {
    'enc(tigo-3fx|tigo3fx|tigo_3fx)': {'this is a test': 'BAYhcO+OwAf3t1VMm/+Ow8ZfcRWX', 'test': 'BA43BFXX', '': ''},
    'dec(tigo-3fx)': {'BA43BFXX': 'test', 'BA43BFX': None, 'BA43@FXX': None},
    'enc-dec(tigo-3fx)': ['this is a test', 'Hello, World! 1234', '\xe9t\xe9 \u2603 \U0001f600', '100% sure', 'a'],
}
__guess__ = ["tigo-3fx"]


add("tigo-3fx", *js_base64("tigo-3fx", "FrsxyzA8VtuvwDEqWZ/1+4klm67=cBCa5Ybdef0g2hij9nopMNO3GHIRSTJKLPQUX"),
    r"^tigo[-_]?3fx$", printables_rate=1., expansion_factor=(1.6, .3))
