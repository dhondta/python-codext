# -*- coding: UTF-8 -*-
"""FERON-74 Codec - FERON-74 content encoding.

FERON-74 is a toy encoding found on online JavaScript encryption tools. It is Base64 with a shuffled alphabet, whose
 65th character ("4") is used for padding. As in the original JavaScript, the text is first escaped with JavaScript's
 escape() (e.g. " " becoming "%20" and "é" becoming "%E9"), and unescaped after decoding ; encoded texts made without
 this escaping (i.e. from the UTF-8 bytes of the text) are then decoded the same way.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: http://qbarbe.free.fr/crypto/eng_feron74c.php
"""
from ._jsbase64 import js_base64
from ..__common__ import add


__examples__ = {
    'enc(feron74|feron-74|feron_74)': {'this is a test': "sbxMC161WbyZ/rSiNq61WcDyCnA4", 'test': "sbRZs744", '': ""},
    'dec(feron74)': {'sbRZs744': "test", 'sbRZ s744': "test", 'sbRZs74': None, 'sbRZs74%': None},
    'enc-dec(feron74)': ["this is a test", "Hello, World! 1234", "\xe9t\xe9 ☃ \U0001F600", "100% sure", "a"],
}
__guess__ = ["feron74"]


add("feron74", *js_base64("feron74", "75XYTabcS/UVWdefADqr6RuvN8PBCsQtwx2KLyz+OM3Hk9ghi01ZFlmnjopE=GIJ4"),
    r"^feron[-_]?74$", printables_rate=1., expansion_factor=(1.6, .3))
