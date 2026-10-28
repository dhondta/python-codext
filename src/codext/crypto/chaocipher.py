# -*- coding: UTF-8 -*-
"""Chaocipher Codec - chaocipher content encoding.

The Chaocipher was invented by John F. Byrne in 1918 and only disclosed in 2010. It uses two alphabets, the left one for
 the ciphertext and the right one for the plaintext. Each letter is replaced by the letter at the same position in the
 other alphabet, then both alphabets are permuted:
- the left one is rotated so that the ciphertext letter comes first, then its second letter is moved to the 14th
   position (the nadir)
- the right one is rotated so that the plaintext letter comes last, then its third letter is moved to the 14th
   position

The alphabets are given as keywords (without duplicates) followed by the remaining letters ; by default, those of the
 example of Moshe Rubin's paper are used. Other characters are kept in place, as well as the case of the letters.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: http://www.chaocipher.com/ActualChaocipher/Chaocipher-Revealing-Algorithm-Rubin.pdf
"""
from string import ascii_lowercase as LC, ascii_uppercase as UC

from ..__common__ import *


__examples__ = {
    'enc(chaocipher|chao-cipher|chao_cipher-hxuczvamdslkpefjrigtwobnyq-ptlnbqdeoysfavzkgjrihwxumc)': {
        'WELLDONEISBETTERTHANWELLSAID': "OAHQHCNYNXTSZJRRHJBYHQKSOUJY"},
    'dec(chaocipher)':                    {'OAHQHCNYNXTSZJRRHJBYHQKSOUJY': "WELLDONEISBETTERTHANWELLSAID"},
    'enc(chaocipher)':                    {'Well done, is better than well said!':
                                           "Oahq hcny, nx tszjrr hjby hqks oujy!"},
    'enc(chaocipher-left-right)':         {'WELLDONEISBETTERTHANWELLSAID': "WGJIAWXFBUWJDBXIRKQYXTNKOGFQ"},
    'enc-dec(chaocipher|chaocipher-left-right|chaocipher-byrne-chaos)': ["", "Hello, World!", "ATTACK AT DAWN",
                                                                         "@random"],
}
__guess__ = ["chaocipher"]


LEFT, RIGHT = "HXUCZVAMDSLKPEFJRIGTWOBNYQ", "PTLNBQDEOYSFAVZKGJRIHWXUMC"


def __alphabet(keyword):
    a = []
    for c in keyword.upper() + UC:
        if c not in a:
            a.append(c)
    return "".join(a)


def __chaocipher(decode=False):
    def _wrapper(left=None, right=None):
        left, right = (__alphabet(left), __alphabet(right)) if left else (LEFT, RIGHT)
        def _code(text, errors="strict"):
            l, r, out = left, right, []
            for c in ensure_str(text):
                if c not in LC and c not in UC:
                    out.append(c)
                    continue
                # the ciphertext letter (left) and the plaintext letter (right) are at the same position
                i = (r if not decode else l).index(c.upper())
                o = (l if not decode else r)[i]
                out.append(o.lower() if c in LC else o)
                # left alphabet: ciphertext letter first, then the 2nd letter moved to the nadir
                l = l[i:] + l[:i]
                l = l[0] + l[2:14] + l[1] + l[14:]
                # right alphabet: plaintext letter last, then the 3rd letter moved to the nadir
                r = r[i+1:] + r[:i+1]
                r = r[:2] + r[3:14] + r[2] + r[14:]
            return (s := "".join(out)), len(s)
        return _code
    return _wrapper


add("chaocipher", __chaocipher(), __chaocipher(True),
    r"^chao(?:[-_]?cipher)?(?:[-_]([a-zA-Z]+)[-_]([a-zA-Z]+))?$", penalty=.1)
