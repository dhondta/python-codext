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


__examples__ = {
    'enc(beaufort)':             None,
    'enc(beaufort-lemon)':       {'ATTACKATDAWN': 'LLTOLBETLNPR'},
    'enc(beaufort-key)':         {'hello': 'danzq'},
    'enc(beaufort_key)':         {'Hello World': 'Danzq Cwnnh'},
    'enc-dec(beaufort-secret)':  ['hello world', 'ATTACK AT DAWN', 'Test 1234!'],
    'enc(vigenere)':             None,
    'enc(vigenere-lemon)':       {'ATTACKATDAWN': 'LXFOPVEFRNHR'},
    'enc(vigenere-key)':         {'hello': 'rijvs'},
    'enc(vigenère_key)':         {'Hello World': 'Rijvs Uyvjn'},
    'enc-dec(vigenere-secret)':  ['hello world', 'ATTACK AT DAWN', 'Test 1234!'],
}
__guess__ = ["beaufort-key", "beaufort-secret", "beaufort-password",
             "vigenere-key", "vigenere-secret", "vigenere-password"]


def __make(encoding, char_func):
    def code(decode=False):
        def _code(key):
            def _wrapper(text, errors="strict"):
                k = key.lower()
                if not k or not k.isalpha():
                    raise LookupError(f"Bad parameter for encoding '{encoding}': key must be a non-empty alphabetic string")
                result, i = [], 0
                for c in ensure_str(text):
                    if c in LC or c in UC:
                        result.append(char_func(c, k, i, decode))
                        i += 1
                    else:
                        result.append(c)
                r = "".join(result)
                return r, len(r)
            return _wrapper
        return _code
    return code(), code(True)


bchar = lambda c, k, i, d=False: (LC if (b := c in LC) else UC)[(ord(k[i % len(k)]) - ord('a') - \
                                                                 (ord(c) - ord("Aa"[b]))) % 26]
add("beaufort", *__make("beaufort", bchar), r"beaufort(?:[-_]cipher)?(?:[-_]([a-zA-Z]+))?$", penalty=.1)

vchar = lambda c, k, i, d=False: (LC if (b := c in LC) else UC)[(ord(c) - ord("Aa"[b]) + \
                                                                 [1, -1][d] * (ord(k[i % len(k)]) - ord('a'))) % 26]
add("vigenere", *__make("vigenere", vchar), r"vigen[eè]re(?:[-_]cipher)?(?:[-_]([a-zA-Z]+))?$", penalty=.1)

