# -*- coding: UTF-8 -*-
"""MEGAN-35 Codec - MEGAN-35 content encoding.

MEGAN-35 is a toy encoding found on online JavaScript encryption tools. It is Base64 with a shuffled alphabet, whose
 65th character ("5") is used for padding. As in the original JavaScript, the text is first escaped with JavaScript's
 escape() (e.g. " " becoming "%20" and "é" becoming "%E9"), and unescaped after decoding ; encoded texts made without
 this escaping (i.e. from the UTF-8 bytes of the text, e.g. by https://gist.github.com/tunelko/49b7e64c1688d62d0ecd)
 are decoded as well, except that an ASCII text holding escape sequences (e.g. "%41") is then unescaped.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://gist.github.com/tunelko/49b7e64c1688d62d0ecd
"""
from ._jsbase64 import js_base64
from ..__common__ import add


__examples__ = {
    'enc(megan35|megan-35|megan_35)': {'this is a test': 'nLX0msesRL1tOdNqicesRM=1mxb5', 'test': 'nLftn355', '': ''},
    'dec(megan35)': {'nLftn355': 'test', 'nLftn35': None, 'nLft@355': None},
    'enc-dec(megan35)': ['this is a test', 'Hello, World! 1234', '\xe9t\xe9 \u2603 \U0001f600', '100% sure', 'a'],
}
__guess__ = ["megan35"]


add("megan35", *js_base64("megan35", "3GHIJKLMNOPQRSTUb=cdefghijklmnopWXYZ/12+406789VaqrstuvwxyzABCDEF5"),
    r"^megan[-_]?35$", printables_rate=1., expansion_factor=(1.6, .3))
