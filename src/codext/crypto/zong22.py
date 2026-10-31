# -*- coding: UTF-8 -*-
"""ZONG22 Codec - ZONG22 content encryption.

ZONG22 is a toy cipher found on online JavaScript encryption tools. It is Base64 with a shuffled alphabet, whose 65th
 character ("2") is used for padding. As in the original JavaScript, the text is first escaped with JavaScript's
 escape() (e.g. " " becoming "%20" and "é" becoming "%E9"), and unescaped after decoding ; ciphertexts made without this
 escaping (i.e. from the UTF-8 bytes of the text, e.g. by https://gist.github.com/tunelko/49b7e64c1688d62d0ecd) are
 decoded as well, except that an ASCII text holding escape sequences (e.g. "%41") is then unescaped.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: http://qbarbe.free.fr/crypto/eng_zong22e.php
"""
from ._jsbase64 import js_base64
from ..__common__ import add


__examples__ = {
    'enc(zong22|zong-22|zong_22)': {'this is a test': 'PyglpexeXyNFwd0QIbxeXfYNpz52', 'test': 'PySFPZ22', '': ''},
    'dec(zong22)': {'PySFPZ22': 'test', 'PySFPZ2': None, 'PySF@Z22': None},
    'enc-dec(zong22)': ['this is a test', 'Hello, World! 1234', '\xe9t\xe9 \u2603 \U0001f600', '100% sure', 'a'],
}
__guess__ = ["zong22"]


add("zong22", *js_base64("zong22", "ZKj9n+yf0wDVX1s/5YbdxSo=ILaUpPBCHg8uvNO4klm6iJGhQ7eFrWczAMEq3RTt2"),
    r"^zong[-_]?22$", printables_rate=1., expansion_factor=(1.6, .3))
