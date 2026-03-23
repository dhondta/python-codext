# -*- coding: UTF-8 -*-
"""VIC Cipher Codec - vic content encoding.

The VIC cipher is a complex manual cipher used by Soviet spies. It combines a
straddling checkerboard substitution (converting letters to a stream of digits)
with a double columnar transposition applied to that digit stream.

The straddling checkerboard uses a keyword-mixed alphabet laid out in a 3-row
grid with two blank positions (default: columns 2 and 6) in the top row.
Letters in the top row get single-digit codes; letters in the two lower rows
get two-digit codes whose first digit is the blank-column header, making the
encoding self-synchronising.

Parameters:
  keyword   : phrase to build the mixed alphabet for the checkerboard
  trans1key : first columnar-transposition key (letters or digits)
  trans2key : second columnar-transposition key (defaults to trans1key)

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://www.dcode.fr/vic-cipher
"""
from ..__common__ import *


__examples__ = {
    'enc-dec(vic-python-352)':     ['HELLO', 'ATTACKATDAWN', 'TEST', ''],
    'enc-dec(vic-python-352-461)': ['HELLO', 'ATTACKATDAWN', 'TEST'],
}
__guess__ = []


# Positions in the top row (0-9) that are left blank; their values become the
# row-header digits for the two lower rows of the checkerboard.
_BLANKS = (2, 6)


def _mixed_alpha(keyword):
    """Return the 26-letter mixed alphabet derived from *keyword*."""
    seen, result = set(), []
    for c in keyword.upper():
        if c.isalpha() and c not in seen:
            result.append(c)
            seen.add(c)
    for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        if c not in seen:
            result.append(c)
    return result


def _build_checkerboard(keyword):
    """Build encode/decode lookup tables for the straddling checkerboard.

    Layout with blanks=(2,6):
      col:  0  1  [2]  3  4  5  [6]  7  8  9
      row0: *  *       *  *  *       *  *  *   (8 single-digit codes)
      row2: *  *  *    *  *  *  *    *  *  *   (10 two-digit codes 2x)
      row6: *  *  *    *  *  *  *    *          (8 two-digit codes 6x)
    """
    alpha = _mixed_alpha(keyword)
    b0, b1 = _BLANKS
    enc, dec, ai = {}, {}, 0
    # Top row – 8 positions
    for col in range(10):
        if col not in _BLANKS:
            enc[alpha[ai]] = str(col)
            dec[str(col)] = alpha[ai]
            ai += 1
    # Second row – 10 positions, header digit = b0
    for col in range(10):
        code = str(b0) + str(col)
        enc[alpha[ai]] = code
        dec[code] = alpha[ai]
        ai += 1
    # Third row – remaining 8 positions, header digit = b1
    for col in range(8):          # 26 total – 8 top-row – 10 second-row = 8 remaining
        code = str(b1) + str(col)
        enc[alpha[ai]] = code
        dec[code] = alpha[ai]
        ai += 1
    return enc, dec


def _col_order(key):
    """Return column indices sorted by the character value of *key* (stable)."""
    return [i for _, i in sorted(zip(key, range(len(key))))]


def _trans_encode(text, key):
    """Columnar transposition: write row-by-row, read column-by-column in key order."""
    k, n = len(key), len(text)
    if n == 0 or k == 0:
        return text
    order = _col_order(key)
    result = []
    for col in order:
        i = col
        while i < n:
            result.append(text[i])
            i += k
    return ''.join(result)


def _trans_decode(text, key):
    """Reverse columnar transposition."""
    k, n = len(key), len(text)
    if n == 0 or k == 0:
        return text
    order = _col_order(key)
    full_rows, remainder = n // k, n % k
    cols = [None] * k
    idx = 0
    for col in order:
        col_len = full_rows + (1 if col < remainder else 0)
        cols[col] = list(text[idx:idx + col_len])
        idx += col_len
    result = []
    for row in range(full_rows + (1 if remainder else 0)):
        for col in range(k):
            if row < len(cols[col]):
                result.append(cols[col][row])
    return ''.join(result)


def vic_encode(keyword, trans1, trans2):
    enc_map, _ = _build_checkerboard(keyword)
    # The framework converts pure-digit groups to int; convert back to str
    t1 = str(trans1)
    t2 = str(trans2) if trans2 else t1

    def encode(text, errors="strict"):
        _h = handle_error("vic", errors)
        digits = []
        for pos, c in enumerate(ensure_str(text).upper()):
            if c in enc_map:
                digits.append(enc_map[c])
            else:
                digits.append(_h(c, pos, ''.join(digits)))
        digit_str = ''.join(d for d in digits if d)
        step1 = _trans_encode(digit_str, t1)
        step2 = _trans_encode(step1, t2)
        return step2, len(step2)

    return encode


def vic_decode(keyword, trans1, trans2):
    _, dec_map = _build_checkerboard(keyword)
    b_set = {str(b) for b in _BLANKS}
    # The framework converts pure-digit groups to int; convert back to str
    t1 = str(trans1)
    t2 = str(trans2) if trans2 else t1

    def decode(text, errors="strict"):
        _h = handle_error("vic", errors, decode=True)
        t = ensure_str(text)
        step1 = _trans_decode(t, t2)
        digit_str = _trans_decode(step1, t1)
        result, i = [], 0
        while i < len(digit_str):
            d = digit_str[i]
            if d in b_set:
                code = digit_str[i:i + 2]
                if code in dec_map:
                    result.append(dec_map[code])
                    i += 2
                else:
                    result.append(_h(code, i, ''.join(result)))
                    i += 2
            elif d in dec_map:
                result.append(dec_map[d])
                i += 1
            else:
                result.append(_h(d, i, ''.join(result)))
                i += 1
        r = ''.join(c for c in result if c)
        return r, len(r)

    return decode


add("vic", vic_encode, vic_decode,
    r"^vic[-_]([a-zA-Z]+)[-_]([a-zA-Z0-9]+)(?:[-_]([a-zA-Z0-9]+))?$")
