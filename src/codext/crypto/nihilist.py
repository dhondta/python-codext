# -*- coding: UTF-8 -*-
"""Nihilist Cipher Codec - nihilist content encoding.

The Nihilist cipher was used by the Russian Nihilists in the 1880s. Each letter of the text and of the key is replaced
 by its coordinates (row and column, from 1 to 5) in a 5x5 Polybius square (I and J sharing a cell), read as a
 two-digit number. The ciphertext is made of the sums of the numbers of the text and of the repeated key. The square is
 filled with an optional keyword (without duplicates), then with the remaining letters of the alphabet.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Nihilist_cipher
"""
from string import ascii_uppercase as UC

from ..__common__ import *


__examples__ = {
    'enc(nihilist)':                      None,
    'dec(nihilist-cipher)':               None,
    'enc(nihilist-zebras-russian)':       {'DYNAMITE WINTER PALACE': "37 106 62 36 67 47 86 26 104 53 62 77 27 55 "
                                                                     "57 66 55 36 54 27", 'Jump!': None},
    'dec(nihilist_cipher-zebras-russian)': {'37 106 62 36 67 47 86 26 104 53 62 77 27 55 57 66 55 36 54 27':
                                            "DYNAMITEWINTERPALACE", '37 10a': None, '37 107': None},
    'enc(nihilist-key)':                  {'Hello': "48 30 85 56 49"},
    'enc-dec(nihilist-key|nihilist-cipher-secret|nihilist-keyword-russian)': ["", "HELLOWORLD", "ATTACKATDAWN"],
}
__guess__ = []


_ALPHABET = UC.replace("J", "")


def __set_params(square_key, key):
    # with a single keyword, this is the key and the square is not keyed
    square_key, key = (str(square_key or ""), str(key)) if key else ("", str(square_key or ""))
    if not key:
        raise LookupError("Bad parameter for encoding 'nihilist': a key is required")
    square = []
    for c in (square_key + _ALPHABET).upper().replace("J", "I"):
        if c not in square:
            square.append(c)
    enc = {c: 10 * (i // 5 + 1) + i % 5 + 1 for i, c in enumerate(square)}
    return enc, {v: k for k, v in enc.items()}, [enc[c] for c in key.upper().replace("J", "I")]


def __nihilist(decode=False):
    def _wrapper(square_key=None, key=None):
        # bad parameters are only reported when coding, as the lookup of the bare codec name must succeed (e.g. when
        #  listing the encodings)
        try:
            params = __set_params(square_key, key)
        except LookupError as e:
            params = e
        def _code(text, errors="strict"):
            if isinstance(params, LookupError):
                raise params
            enc, dec, key = params
            text, r = ensure_str(text), []
            if decode:
                _h = handle_error("nihilist", errors, decode=True, kind="token")
                for i, t in enumerate(text.split()):
                    # a token that is not a number, or that does not give a cell of the square, cannot be decoded
                    r.append(dec.get(int(t) - key[i % len(key)], None) if t.isdigit() else None)
                    if r[-1] is None:
                        r[-1] = _h(t, i, "".join(r[:-1]))
            else:
                # whitespaces are ignored ; the replacement character is encrypted too
                _h = handle_error("nihilist", errors, repl_char="X")
                for i, c in enumerate(text.upper().replace("J", "I")):
                    if c in enc:
                        r.append(c)
                    elif not c.isspace():
                        r.extend(x for x in _h(c, i) if x in enc)
                r = [str(enc[c] + key[i % len(key)]) for i, c in enumerate(r)]
            return (s := ("" if decode else " ").join(r)), len(s)
        return _code
    return _wrapper


add("nihilist", __nihilist(), __nihilist(True),
    r"^nihilist(?:[-_]cipher)?(?:[-_]([a-zA-Z]+))?(?:[-_]([a-zA-Z]+))?$", penalty=.1)
