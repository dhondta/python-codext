# -*- coding: UTF-8 -*-
"""Bazeries Cipher Codec - bazeries content encoding.

The Bazeries cipher is an encryption system created by Étienne Bazeries that combines
two Polybius grids (5×5 square arrays of letters) and a transposition based on a
numeric key. The plaintext is split into groups whose sizes are the digits of the key,
each group is reversed, and then a substitution is applied by mapping each letter's
position in the first (standard) Polybius square to the same position in the second
(key-based) Polybius square. When the key is a keyword instead of a number, the
lengths of the words in the keyword are used as group sizes.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://www.dcode.fr/bazeries-cipher
"""
from ..__common__ import *


__examples__ = {
    'enc(bazeries-137)': {'HELLO': 'TSSUB', 'ATTACK': 'OOLLYE'},
    'dec(bazeries-137)': {'TSSUB': 'HELLO', 'OOLLYE': 'ATTACK'},
}
__guess__ = ["bazeries-137"]


_DEFAULT_KEY = "137"
# Standard 5×5 Polybius square alphabet (I and J share the same cell)
_DEFAULT_ALPHABET = "ABCDEFGHIKLMNOPQRSTUVWXYZ"

_ONES = ["", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE",
         "TEN", "ELEVEN", "TWELVE", "THIRTEEN", "FOURTEEN", "FIFTEEN", "SIXTEEN",
         "SEVENTEEN", "EIGHTEEN", "NINETEEN"]
_TENS = ["", "", "TWENTY", "THIRTY", "FORTY", "FIFTY", "SIXTY", "SEVENTY", "EIGHTY", "NINETY"]


def _num_to_words(n):
    """ Convert a non-negative integer to its English word representation (uppercase). """
    if n == 0:
        return "ZERO"
    if n < 20:
        return _ONES[n]
    if n < 100:
        rest = n % 10
        return (_TENS[n // 10] + (" " + _ONES[rest] if rest else "")).strip()
    if n < 1000:
        rest = n % 100
        return (_ONES[n // 100] + " HUNDRED" + (" " + _num_to_words(rest) if rest else "")).strip()
    if n < 1_000_000:
        rest = n % 1000
        return (_num_to_words(n // 1000) + " THOUSAND" + (" " + _num_to_words(rest) if rest else "")).strip()
    if n < 1_000_000_000:
        rest = n % 1_000_000
        return (_num_to_words(n // 1_000_000) + " MILLION" + (" " + _num_to_words(rest) if rest else "")).strip()
    rest = n % 1_000_000_000
    return (_num_to_words(n // 1_000_000_000) + " BILLION" + (" " + _num_to_words(rest) if rest else "")).strip()


def _parse_key(key):
    """ Parse the key into (phrase, group_sizes).

    For a numeric key, it is written in English words to build the phrase, and its
    individual non-zero digits form the group sizes for transposition.
    For a keyword, the key itself is the phrase and word lengths are the group sizes.
    """
    if not key:
        key = _DEFAULT_KEY
    key_str = str(key).upper().replace("-", " ").replace("_", " ").strip()
    if key_str.replace(" ", "").isdigit():
        n = int(key_str.replace(" ", ""))
        phrase = _num_to_words(n)
        digits = [int(d) for d in str(n) if d != '0']
        if not digits:
            digits = [1]
    else:
        phrase = key_str
        digits = [len(w) for w in key_str.split() if w]
        if not digits:
            digits = [1]
    return phrase, digits


def _build_key_alphabet(phrase):
    """ Build a 25-character cipher alphabet from the key phrase for the second Polybius square.

    Letters appear in the order they first occur in the phrase (with J merged into I),
    followed by the remaining letters of the standard alphabet.
    """
    seen = []
    for c in phrase.upper():
        if c == 'J':
            c = 'I'
        if c.isalpha() and c not in seen:
            seen.append(c)
    for c in _DEFAULT_ALPHABET:
        if c not in seen:
            seen.append(c)
    return "".join(seen)


def _build_squares(key_alphabet):
    """ Build position maps and lookup maps for the two 5×5 Polybius squares.

    Returns (sq1_pos, sq2_pos, sq1_lkp, sq2_lkp) where:
      - sq1_pos / sq2_pos map a letter to its (row, col) 1-indexed coordinate
      - sq1_lkp / sq2_lkp map a (row, col) coordinate to its letter
    """
    alph1 = _DEFAULT_ALPHABET
    alph2 = key_alphabet
    sq1_pos = {alph1[i]: (i // 5 + 1, i % 5 + 1) for i in range(25)}
    sq2_pos = {alph2[i]: (i // 5 + 1, i % 5 + 1) for i in range(25)}
    sq1_lkp = {(i // 5 + 1, i % 5 + 1): alph1[i] for i in range(25)}
    sq2_lkp = {(i // 5 + 1, i % 5 + 1): alph2[i] for i in range(25)}
    # J shares the cell with I in both squares
    sq1_pos['J'] = sq1_pos['I']
    sq2_pos['J'] = sq2_pos['I']
    return sq1_pos, sq2_pos, sq1_lkp, sq2_lkp


def _transpose(chars, digits):
    """ Split chars into consecutive groups of sizes given by digits (cycling) and reverse each group. """
    result, i, grp_idx = [], 0, 0
    while i < len(chars):
        size = digits[grp_idx % len(digits)]
        grp_idx += 1
        group = chars[i:i + size]
        result.extend(reversed(group))
        i += size
    return result


def bazeries_encode(key=""):
    phrase, digits = _parse_key(key)
    key_alph = _build_key_alphabet(phrase)
    sq1_pos, sq2_pos, sq1_lkp, sq2_lkp = _build_squares(key_alph)

    def encode(text, errors="strict"):
        _h = handle_error("bazeries", errors)
        alpha = [('I' if c == 'J' else c) for c in ensure_str(text).upper() if c.isalpha()]
        transposed = _transpose(alpha, digits)
        result = []
        for pos, c in enumerate(transposed):
            if c in sq1_pos:
                result.append(sq2_lkp[sq1_pos[c]])
            else:
                result.append(_h(c, pos, "".join(result)))
        r = "".join(result)
        return r, len(text)
    return encode


def bazeries_decode(key=""):
    phrase, digits = _parse_key(key)
    key_alph = _build_key_alphabet(phrase)
    sq1_pos, sq2_pos, sq1_lkp, sq2_lkp = _build_squares(key_alph)

    def decode(text, errors="strict"):
        _h = handle_error("bazeries", errors, decode=True)
        alpha = [c for c in ensure_str(text).upper() if c.isalpha()]
        sub = []
        for pos, c in enumerate(alpha):
            if c in sq2_pos:
                sub.append(sq1_lkp[sq2_pos[c]])
            else:
                sub.append(_h(c, pos, "".join(sub)))
        result = _transpose(sub, digits)
        r = "".join(result)
        return r, len(text)
    return decode


add("bazeries", bazeries_encode, bazeries_decode,
    r"^bazeries(?:[-_](.+))?$",
    printables_rate=1., expansion_factor=1.)
