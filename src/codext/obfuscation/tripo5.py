# -*- coding: UTF-8 -*-
"""TRIPO-5 Codec - TRIPO-5 content encoding.

TRIPO-5 is a toy encoding found on online JavaScript encryption tools. It is Base64 with a shuffled alphabet, whose 65th
 character ("T") is used for padding. As in the original JavaScript, the text is first escaped with JavaScript's
 escape() (e.g. " " becoming "%20" and "é" becoming "%E9"), and unescaped after decoding ; encoded texts made without
 this escaping (i.e. from the UTF-8 bytes of the text) are decoded as well, except that an ASCII text holding escape
 sequences (e.g. "%41") is then unescaped.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: http://qbarbe.free.fr/crypto/eng_tripo5e.php
"""
from ._jsbase64 import js_base64
from ..__common__ import add


__examples__ = {
    'enc(tripo-5|tripo5|tripo_5)': {'this is a test': 'dEBqW2=2mE5K7YGwSX=2m+R5W0QT', 'test': 'dEaKdgTT', '': ''},
    'dec(tripo-5)': {'dEaKdgTT': 'test', 'dEaKdgT': None, 'dEaK@gTT': None},
    'enc-dec(tripo-5)': ['this is a test', 'Hello, World! 1234', '\xe9t\xe9 \u2603 \U0001f600', '100% sure', 'a'],
}
__guess__ = ["tripo-5"]


add("tripo-5", *js_base64("tripo-5", "ghijopE+G78lmnIJQRXY=abcS/UVWdefABCs456tDqruvNOPwx2KLyz01M3Hk9ZFT"),
    r"^tripo[-_]?5$", printables_rate=1., expansion_factor=(1.6, .3))
