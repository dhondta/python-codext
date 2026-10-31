# -*- coding: UTF-8 -*-
"""ESAB-46 Codec - ESAB-46 content encoding.

ESAB-46 ("Base-64" reversed) is a toy encoding found on online JavaScript encryption tools. It is Base64 with a shuffled
 alphabet, whose 65th character ("/") is used for padding. As in the original JavaScript, the text is first escaped with
 JavaScript's escape() (e.g. " " becoming "%20" and "é" becoming "%E9"), and unescaped after decoding ; encoded texts
 made without this escaping (i.e. from the UTF-8 bytes of the text) are then decoded the same way.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://crypo.tonylao.com/esab46c.htm
"""
from ._jsbase64 import js_base64
from ..__common__ import add


__examples__ = {
    'enc(esab46|esab-46|esb46|esb_46)': {'this is a test': "9sRZ8i0ivsVj6z5gLy0iv4xV8nw/", 'test': "9s1j9A//", '': ""},
    'dec(esab46)': {'9s1j9A//': "test", '9s1j 9A//': "test", '9s1j9A/': None, '9s1j9A/%': None},
    'enc-dec(esab46)': ["this is a test", "Hello, World! 1234", "\xe9t\xe9 ☃ \U0001F600", "100% sure", "a"],
}
__guess__ = ["esab46"]


add("esab46", *js_base64("esab46", "ABCDqrs456tuvNOPwxyz012KLM3789=+QRSTUVWXYZabcdefghijklmnopEFGHIJ/"),
    r"^esa?b[-_]?46$", printables_rate=1., expansion_factor=(1.6, .3))
