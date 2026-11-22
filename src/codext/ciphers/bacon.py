# -*- coding: UTF-8 -*-
"""Bacon's Cipher Codec - bacon content encoding.

Bacon's cipher was devised by Francis Bacon in 1605 as a steganographic method: each letter is written as a group of 5
 symbols among two ("a" and "b"), which can then be hidden e.g. in the choice between two typefaces. Two alphabets are
 supported:
- the original 24-letter alphabet (default), in which I and J, as well as U and V, share the same code (decoded as I and
   U) ;
- the 26-letter alphabet ("bacon-26"), in which each letter has its own code (e.g. J is "abaab" and V is "babab").
The two symbols can be chosen in the codec name (e.g. "bacon-01", "bacon-ba" or "bacon-26-01").

When hidden in a cover text, each letter of this text carries one symbol, hence the spaces of the encoded text are the
 ones of the cover text and do not fall on the groups of 5 symbols. When decoding, if a space-separated group is not
 made of a multiple of 5 symbols, the spaces are considered as the ones of a cover text: they are removed and the last
 incomplete group, made of the remaining letters of the cover text, is ignored.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Bacon%27s_cipher
           https://www.dcode.fr/bacon-cipher
"""
from ..__common__ import *


__examples__ = {
    'enc(bacon|bacon_cipher|baconian-cipher|bacon-ab|bacon_AB|bacon-24)': {
        'this is a test': "baabaaabbbabaaabaaab abaaabaaab aaaaa baabaaabaabaaabbaaba",
    },
    'enc(bacon-01|bacon_01|bacon-24-01)': {
        'this is a test': "10010001110100010001 0100010001 00000 10010001001000110010",
    },
    'enc(bacon)': {'jv': "abaaabaabb"},
    'dec(bacon)': {'abaaabaabb': "IU"},
    'dec(bacon-26)': {'BAAB AB AB AAABBBB AA BA A BAAABBAA BAAA BAAAAABA BAA A BAABAA BAABB AA': "SUPERSECRET"},
    'enc(bacon-26|bacon26|bacon_26|baconian-cipher-26)': {
        'this is a test': "baabbaabbbabaaabaaba abaaabaaba aaaaa baabbaabaabaababaabb",
        'jv': "abaabbabab", 'yz': "bbaaabbaab",
    },
    'enc(bacon-26-01|bacon26_01)': {'this is a test': "10011001110100010010 0100010010 00000 10011001001001010011"},
    'enc(bacon-26-ba)': {'jv': "babbaababa"},
    'dec(bacon-26-ab)': {'abaabbabab': "JV", 'baabbaabbbabaaabaaba': "THIS", 'bbbbb': None},
    'enc-dec(bacon-26|bacon-26-01|bacon-26-xy)': ["THIS IS A TEST", "JUMP OVER THE LAZY DOG"],
    'enc(bacon-aa)': None,
    'enc(bacon-26-aa)': None,
}
__guess__ = ["bacon", "bacon-ba", "bacon-01", "bacon-10", "bacon-26", "bacon-26-ba", "bacon-26-01", "bacon-26-10"]


LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
# each letter is its index in the alphabet written with 5 binary symbols ("a" for 0, "b" for 1) ; in the original
#  24-letter alphabet, J and V are not counted, sharing the codes of I and U
_code = lambda n: f"{n:05b}".translate(str.maketrans("01", "ab"))
ENCMAP26 = {c: _code(i) for i, c in enumerate(LETTERS)}
ENCMAP24 = {c: _code(i) for i, c in enumerate(LETTERS.replace("J", "").replace("V", ""))}
ENCMAP24.update(J=ENCMAP24['I'], V=ENCMAP24['U'])
ENCMAP = ENCMAP24  # backward compatibility


def _encmap(param):
    """ Build the encoding map from the parameter of the codec name: the alphabet (24 letters by default, or 26) and the
         two symbols (default: "ab"). """
    # the pattern of the codec name ensures that the parameter has this form ; NB: a parameter made of digits only (e.g.
    #  "26" from "bacon26") is given as an integer
    alphabet, symbols = re.match(r"^(?:[-_]?(2[46]))?(?:[-_](.{2}))?$", "" if param is None else str(param)).groups()
    if symbols is not None and (len(set(symbols)) != 2 or " " in symbols):
        raise LookupError(f"Bad parameter for encoding 'bacon': '{param}'")
    t = str.maketrans("ab", symbols or "ab")
    encmap = {c: code.translate(t) for c, code in (ENCMAP26 if alphabet == "26" else ENCMAP24).items()}
    encmap[' '] = " "
    return encmap


def _cover_text(text):
    """ Remove the spaces of a cover text (when a space-separated group is not made of a multiple of 5 symbols) and its
         last incomplete group. """
    groups = text.split()
    if len(groups) > 1 and any(len(g) % 5 for g in groups):
        text = "".join(groups)
        text = text[:len(text) - len(text) % 5]
    return text


# NB: the guess list is given explicitly, as add_map does not pass on the one of the module
add_map("bacon", _encmap, ignore_case="both", guess=__guess__, preprocess=_cover_text,
        pattern=r"^bacon(?:(?:ian)?[-_]cipher)?(|[-_]?2[46](?:[-_].{2})?|[-_].{2})$", expansion_factor=5.,
        printables_rate=1.)
