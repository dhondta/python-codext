# -*- coding: UTF-8 -*-
"""Vic Cipher Codec - vic content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from itertools import cycle
from string import ascii_uppercase as UC

from ..__common__ import *


__examples__ = {
    'dec(vic-test-33)':         None,
    'dec(vic-*-12-1234T':       {'BBXMBDMBCBBHEMC': "THISISATEST"},
    'dec(vic-^-26-0248T)':      {'VVXYWYY.XYJ': "VICTOR2"},  # '2' because of superfluous extra letter from substitution
    'enc(vic-test-12-ABC)':     None,
    'enc(vic-*-12-1234T':       {'This is a Test': "BBXMBDMBCBBHEMC"},
    'enc(vic-^-26-0248)':       {'VICTOR': "88547440546"},
    'enc(vic-^-26-0248T)':      {'VICTOR': "VVXYWYY.XYJ"},
    'enc-dec(vic-^-26)':        ["TEST", "LONGTESTSTRING", "VICTOR"],
    'enc-dec(vic-^-85-72564)':  ["TEST", "LONGTESTSTRING", "VICTOR"],
    'enc-dec(vic-^-85-54321T)': ["TEST", "LONGTESTSTRING", "VICTOR"],
}
__guess__ = ["vic"]


def __build_alphabet(key, alphabet=UC, reverse=False):
    """Return the 28-letter alphabet derived from the input key."""
    seen, result = set(), ""
    for c in (key or "").upper():
        if c.isalpha() and c not in seen:
            result += c
            seen.add(c)
    for c in (alphabet[::-1] if reverse else alphabet):
        if c not in seen:
            result += c
    return "./" + result if reverse else result + "./"


def __build_checkerboard(alphabet, blank1=1, blank2=2):
    """Build encode/decode lookup tables for the straddling checkerboard.

    Layout with digit1=2 and digit2=6:
         0  1 [2] 3  4  5 [6] 7  8  9
      0: *  *     *  *  *     *  *  *
      2: *  *  *  *  *  *  *  *  *  *
      6: *  *  *  *  *  *  *  *  *  *
    """
    if blank1 == blank2:
        raise LookupError(f"Bad parameter for encoding 'vic': blank1 and blank2 cannot be identical")
    enc, dec, i = {}, {}, 0
    # top row
    for col in range(10):
        if col not in (blank1, blank2):
            enc[alphabet[i]] = str(col)
            i += 1
    # second row ; header digit is 'blank1'
    for col in range(10):
        enc[alphabet[i]] = str(blank1) + str(col)
        i += 1
    # third row ; header digit is 'blank2'
    for col in range(10):
        enc[alphabet[i]] = str(blank2) + str(col)
        i += 1
    return enc, {v: k for k, v in enc.items()}


def __set_params(key, blanks, numeric_key):
    return (UC if key == "*" else UC[::-1] if key == "^" else key).upper(), \
           tuple(map(int, str(blanks) or "12")), \
           str(numeric_key or "").rstrip("T"), \
           key == "^", \
           str(numeric_key or " ")[-1] == "T"


def vic_encode(key=None, blanks=None, numeric_key=None):
    key, blanks, numeric_key, rev, txt = __set_params(key, blanks, numeric_key)
    enc_map, dec_map = __build_checkerboard(__build_alphabet(key, reverse=rev), blanks[0], blanks[1])
    def _encode(text, errors="strict"):
        _h = handle_error("vic", errors)
        digits, nk_i, nk_l = [], 0, len(numeric_key or "")
        for pos, c in enumerate(ensure_str(text).upper().replace(" ", "")):
            # 1) encode with the straddling checkerboard
            c = enc_map[c] if c in enc_map else _h(c, pos, "".join(digits))
            # 2) if numeric_key is defined, over-encrypt digits
            if numeric_key and c.isdigit():
                for ci in c:
                    digits.append(str((int(ci) + int(numeric_key[nk_i % nk_l])) % 10))
                    nk_i += 1
            else:
                digits.append(c)
        r = "".join(d for d in digits if d)
        # 3) if text mode, convert digits to text
        if txt:
            i, r0, l, r = 0, r, len(r), ""
            while i < len(r0):
                if int(r0[i]) in blanks:
                    r += dec_map[r0[i] + ("0" if i == l - 1 else r0[i+1])]
                    i += 1
                else:
                    r += dec_map[r0[i]]
                i += 1
        return r, len(r)
    return _encode


def vic_decode(key=None, blanks=None, numeric_key=None):
    key, blanks, numeric_key, rev, txt = __set_params(key, blanks, numeric_key)
    enc_map, dec_map = __build_checkerboard(__build_alphabet(key, reverse=rev), blanks[0], blanks[1])
    def _decode(text, errors="strict"):
        _h = handle_error("vic", errors, decode=True)
        # 1) if text mode, convert text to digits
        text = "".join(enc_map[c] for c in ensure_str(text)) if txt else ensure_str(text)
        # 2) if numeric_key is defined, over-decrypt
        digits, nk_i, nk_l = [], 0, len(numeric_key or "")
        for pos, c in enumerate(text):
            if numeric_key and c.isdigit():
                for ci in c:
                    digits.append(str((int(c) - int(numeric_key[nk_i % nk_l])) % 10))
                    nk_i += 1
            else:
                digits.append(c if c.isdigit() else _h(c, pos, "".join(digits)))
        # 3) decode with the straddling checkerboard
        i, r, r0 = 0, "", "".join(d for d in digits if d)
        while i < (l := len(r0)):
            if int(r0[i]) in blanks:
                r += r0[i] if i == l - 1 else dec_map[r0[i] + r0[i+1]]
                i += 1
            else:
                r += dec_map[r0[i]] if r0[i] in dec_map else _h(r0[i], i, r)
            i += 1
        return r, len(r)
    return _decode


add("vic", vic_encode, vic_decode, r"vic(?:[-_]([\^*]|[./a-zA-Z]+))?(?:[-_]([0-9]{2}))?(?:[-_]([0-9]+T?))?$",
    printables_rate=1., penalty=.1)

