# -*- coding: UTF-8 -*-
"""GILA7 Codec - GILA7 content encoding.

GILA7 is a toy encoding found on online JavaScript encryption tools. It is Base64 with a shuffled alphabet, whose 65th
 character ("G") is used for padding. As in the original JavaScript, the text is first escaped with JavaScript's
 escape() (e.g. " " becoming "%20" and "é" becoming "%E9"), and unescaped after decoding ; encoded texts made without
 this escaping (i.e. from the UTF-8 bytes of the text) are then decoded the same way.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: http://qbarbe.free.fr/crypto/eng_gila7c.php
"""
from ._jsbase64 import js_base64
from ..__common__ import add


__examples__ = {
    'enc(gila7|gila-7|gila_7)': {'this is a test': "3+1QqbzbB+Odcg=5v0zbBWfOqxyG", 'test': "3+Ad37GG", '': ""},
    'dec(gila7)': {'3+Ad37GG': "test", '3+Ad 37GG': "test", '3+Ad37G': None, '3+Ad37G%': None},
    'enc-dec(gila7)': ["this is a test", "Hello, World! 1234", "\xe9t\xe9 ☃ \U0001F600", "100% sure", "a"],
}
__guess__ = ["gila7"]


add("gila7", *js_base64("gila7", "7ZSTJK+W=cVtBCasyf0gzA8uvwDEq3XH/1RMNOILPQU4klm65YbdeFrx2hij9nopG"), r"^gila[-_]?7$",
    printables_rate=1., expansion_factor=(1.6, .3))
