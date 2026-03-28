# -*- coding: UTF-8 -*-
"""Vigenere Cipher Codec - vigenere content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from string import ascii_lowercase as LC, ascii_uppercase as UC

from ..__common__ import *

__examples1__ = {
    'enc(autoclave)':         None,
    'enc(autokey-queenly)':   {'ATTACKATDAWN': 'QNXEPVYTWTWP'},
    'enc-dec(autoclave-key)': ['hello world', 'ATTACK AT DAWN', 'Test 1234!', 'Mixed Case 123'],
}
__examples2__ = {
    'enc(beaufort)':            None,
    'enc(beaufort-lemon)':      {'ATTACKATDAWN': 'LLTOLBETLNPR'},
    'enc(beaufort-key)':        {'hello': 'danzq'},
    'enc(beaufort_key)':        {'Hello World': 'Danzq Cwnnh'},
    'enc-dec(beaufort-secret)': ['hello world', 'ATTACK AT DAWN', 'Test 1234!'],
}
__examples3__ = {
    'enc(trithemius-cipher)': {'this is a test': "tikv mx g ambd"},
    'enc(trithemius)':        {'HELLO': "HFNOS", '12345!@#$': "12345!@#$"},
    'enc-dec(trithemius)':    ["Hello, World!", "@random"],
}
__examples4__ = {
    'enc(vigenere)':            None,
    'enc(vigenere-lemon)':      {'ATTACKATDAWN': 'LXFOPVEFRNHR'},
    'enc(vigenere-key)':        {'hello': 'rijvs'},
    'enc(vigenère_key)':        {'Hello World': 'Rijvs Uyvjn'},
    'enc-dec(vigenere-secret)': ['hello world', 'ATTACK AT DAWN', 'Test 1234!'],
}
__guess1__ = ["autoclave-key", "autoclave-password", "autoclave-secret"]
__guess2__ = ["beaufort-key", "beaufort-password", "beaufort-secret"]
__guess3__ = ["trithemius"]
__guess4__ = ["vigenere-key", "vigenere-password", "vigenere-secret"]


bchar = lambda c, k, i, d=False: (LC if (b := c in LC) else UC)[(ord(k[i % len(k)]) - ord('a') - \
                                                                 (ord(c) - ord("Aa"[b]))) % 26]
vchar = lambda c, k, i, d=False: (LC if (b := c in LC) else UC)[(ord(c) - ord("Aa"[b]) + \
                                                                 [1, -1][d] * (ord(k[i % len(k)]) - ord('a'))) % 26]


def __make(enc, char_func, key_stream=False):
    def _code(decode=False):
        def _wrapper(key):
            def _subwrapper(text, errors="strict"):
                if not (k := key.lower()) or not k.isalpha():
                    raise LookupError(f"Bad parameter for encoding '{enc}': key must be a non-empty alphabetic string")
                if key_stream and not decode:
                    k += "".join(c.lower() for c in ensure_str(text) if c in LC or c in UC)
                result, i = [], 0
                if key_stream and decode:
                    k = list(k)
                for c in ensure_str(text):
                    if c in LC or c in UC:
                        result.append(dc := char_func(c, k, i, decode))
                        if key_stream and decode:
                            k.append(dc.lower())
                        i += 1
                    else:
                        result.append(c)
                return (r := "".join(result)), len(r)
            return _subwrapper
        return _wrapper
    return _code(), _code(True)


add("autoclave", *__make("autoclave", vchar, True), r"auto(?:clave|key)(?:[-_]cipher)?(?:[-_]([a-zA-Z]+))?$",
    examples=__examples1__, guess=__guess1__, penalty=.1)

add("beaufort", *__make("beaufort", bchar), r"beaufort(?:[-_]cipher)?(?:[-_]([a-zA-Z]+))?$",
    examples=__examples2__, guess=__guess2__, penalty=.1)

enc, dec = __make("trithemius", vchar)
add("trithemius", enc(k := "ABCDEFGHIJKLMNOPQRSTUVWXYZ"), dec(k), r"trithemius(?:[-_]cipher)?$",
    examples=__examples3__, guess=__guess3__, penalty=.1)

add("vigenere", *__make("vigenere", vchar), r"vigen[eè]re(?:[-_]cipher)?(?:[-_]([a-zA-Z]+))?$",
    examples=__examples4__, guess=__guess4__, penalty=.1)

