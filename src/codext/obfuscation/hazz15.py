# -*- coding: UTF-8 -*-
"""HAZZ-15 Codec - HAZZ-15 content encoding.

HAZZ-15 is a toy encoding found on online JavaScript encryption tools. It is Base64 with a shuffled alphabet, whose
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
    'enc(hazz15|hazz-15|hazz_15)': {'this is a test': '3m7Vqbzb+mFdjgiGv0zb+6fFq=y5', 'test': '3mAd3H55', '': ''},
    'dec(hazz15)': {'3mAd3H55': 'test', '3mAd3H5': None, '3mAd@H55': None},
    'enc-dec(hazz15)': ['this is a test', 'Hello, World! 1234', '\xe9t\xe9 \u2603 \U0001f600', '100% sure', 'a'],
}
__guess__ = ["hazz15"]


add("hazz15", *js_base64("hazz15", "HNO4klm6ij9n+J2hyf0gzA8uvwDEq3X1Q7ZKeFrWcVTts/MRGYbdxSo=ILaUpPBC5"),
    r"^hazz[-_]?15$", printables_rate=1., expansion_factor=(1.6, .3))
