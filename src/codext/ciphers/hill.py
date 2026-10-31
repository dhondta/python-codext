# -*- coding: UTF-8 -*-
"""Hill Cipher Codec - hill content encoding.

The Hill cipher was invented by Lester S. Hill in 1929. The letters (A=0, ..., Z=25) are taken in blocks of n, each
 block being multiplied (as a column vector) by a n x n key matrix modulo 26. The key matrix is given as a keyword whose
 length is a square (4 letters for a 2x2 matrix, 9 for a 3x3 matrix, ...), filled row by row ; it must be invertible
 modulo 26, that is, its determinant must be coprime with 26.

Other characters are kept in place, as well as the case of the letters. When encoding, the last block is padded with
 "X" ; when decoding, an incomplete last block cannot be decoded.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Hill_cipher
"""
from math import gcd, isqrt
from string import ascii_lowercase as LC, ascii_uppercase as UC

from ..__common__ import *


__examples__ = {
    'enc(hill)':                    None,
    'enc(hill-abc)':                None,
    'enc(hill-abcd)':               None,
    'enc(hill-gybnqkurp)':          {'ACT': "POH", 'CAT': "FIN", 'Cat!': "Fin!", 'CATS': "FINHAE"},
    'dec(hill_cipher-gybnqkurp)':   {'POH': "ACT", 'FIN': "CAT", 'FINE': None},
    'enc(hill-ddcf)':               {'HELP': "HIAT"},
    'dec(hill-cipher-ddcf)':        {'HIAT': "HELP"},
    'enc(hill-invertiblematrix)':   None,
    'enc(hill-aaab)':               None,
    # texts of 12 letters, so that no padding is needed with 2x2, 3x3 and 4x4 matrices
    'enc-dec(hill-ddcf|hill-gybnqkurp|hill-lesterhillcipher)': ["", "Hello, my World", "Attack at dawn!!"],
}
__guess__ = []


def __det(m):
    """ Exact integer determinant with the fraction-free Bareiss algorithm. """
    m, n, sign, prev = [r[:] for r in m], len(m), 1, 1
    for k in range(n - 1):
        if m[k][k] == 0:
            for i in range(k + 1, n):
                if m[i][k] != 0:
                    m[k], m[i], sign = m[i], m[k], -sign
                    break
            else:
                return 0
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                m[i][j] = (m[i][j] * m[k][k] - m[i][k] * m[k][j]) // prev
        prev = m[k][k]
    return sign * m[-1][-1]


def __set_params(key):
    key = str(key or "").upper()
    if (n := isqrt(len(key))) == 0 or n * n != len(key):
        raise LookupError("Bad parameter for encoding 'hill': key length must be a non-null square (4, 9, 16, ...)")
    m = [[ord(c) - 65 for c in key[i*n:(i+1)*n]] for i in range(n)]
    if gcd(d := __det(m) % 26, 26) != 1:
        raise LookupError("Bad parameter for encoding 'hill': key matrix must be invertible modulo 26")
    # inverse matrix: inverse of the determinant times the adjugate (transposed cofactors)
    minor = lambda i, j: [r[:j] + r[j+1:] for k, r in enumerate(m) if k != i]
    adj = [[(-1) ** (i + j) * __det(minor(j, i)) if n > 1 else 1 for j in range(n)] for i in range(n)]
    return m, [[pow(d, -1, 26) * x % 26 for x in r] for r in adj]


def __hill(decode=False):
    def _wrapper(key=None):
        # bad parameters are only reported when coding, as the lookup of the bare codec name must succeed (e.g. when
        #  listing the encodings)
        try:
            params = __set_params(key)
        except LookupError as e:
            params = e
        def _code(text, errors="strict"):
            if isinstance(params, LookupError):
                raise params
            m = params[decode]
            n, text = len(m), ensure_str(text)
            slots = [i for i, c in enumerate(text) if c in LC or c in UC]
            values = [ord(text[i].upper()) - 65 for i in slots]
            r, l = list(text), len(values) - len(values) % n
            if not decode and l < len(values):
                # the last block is padded with "X", appended to the text
                values += [23] * (n - len(values) + l)
                l = len(values)
            out = []
            for b in range(0, l, n):
                out += [sum(m[i][j] * values[b+j] for j in range(n)) % 26 for i in range(n)]
            for k, v in enumerate(out):
                if k < len(slots):
                    r[slots[k]] = (LC if text[slots[k]] in LC else UC)[v]
                else:
                    r.append(UC[v])
            # an incomplete last block cannot be decoded
            _h = handle_error("hill", errors, decode=True)
            for k in slots[l:]:
                r[k] = _h(text[k], k, "".join(r[:k]))
            return (s := "".join(r)), len(s)
        return _code
    return _wrapper


add("hill", __hill(), __hill(True), r"^hill(?:[-_]cipher)?(?:[-_]([a-zA-Z]+))?$", penalty=.1)
