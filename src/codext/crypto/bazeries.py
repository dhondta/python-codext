# -*- coding: UTF-8 -*-
"""Bazeries Cipher Codec - bazeries content encoding.

The Bazeries cipher is an encryption system created by Etienne Bazeries that combines two Polybius grids and a
 transposition based on a numeric key. The first grid holds the alphabet written in columns, the second one is filled in
 rows with the key number written in (English) words, or with a keyword, followed by the remaining letters. The
 plaintext is split into groups whose sizes are the digits of the key (repeated as needed), each group is reversed, and
 each letter is then replaced by the letter at the same position in the second grid.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://www.dcode.fr/bazeries-cipher
"""
from ._square import *
from ..__common__ import *


__examples__ = {
    'enc(bazeries)':                  None,
    'enc(bazeries-0)':                None,
    'enc(bazeries-23-6-ji)':          None,
    'enc(bazeries-23-5-jj)':          None,
    'enc(bazeries-23)':               {'DCODE': "DLSLO", 'dcode': "dlslo"},
    'dec(bazeries-23)':               {'DLSLO': "DCODE"},
    'enc(bazeries_cipher-81257)':     {'SIMPLE SUBSTITUTION PLUS TRANSPOSITION':
                                       "XRMGQN BRYKRBKXKBKR XGQW CBRCQRWEUKCBW"},
    'enc(bazeries-23-keyword)':       {'DCODE': "FMTMP"},
    'enc(bazeries-12,3)':             {'ABCDEFGHIJKLMNOPQRS': "ESKKBRNQIADOLCTFWHV"},
    'enc(bazeries-42-6)':             {'Test 1234!': "DTXD 2UW8!"},
    'enc-dec(bazeries-137)':          ["HELLO", "Hello, World!", "Test 1234!", "Café, ñandú & 10€"],
    'enc-dec(bazeries-3752-jumping)': ["ATTACK AT DAWN", "This is a test"],
    'enc-dec(bazeries-1002003)':      ["ATTACK AT DAWN"],
    'enc-dec(bazeries-105-5-wv)':     ["THIS IS A TEST JUST AS IT IS"],
    'enc-dec(bazeries-42-6)':         ["TEST 1234!", "THE CODE IS 0042"],
}
__guess__ = []


_ONES = ["ZERO", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE", "TEN", "ELEVEN", "TWELVE",
         "THIRTEEN", "FOURTEEN", "FIFTEEN", "SIXTEEN", "SEVENTEEN", "EIGHTEEN", "NINETEEN"]
_TENS = [None, None, "TWENTY", "THIRTY", "FORTY", "FIFTY", "SIXTY", "SEVENTY", "EIGHTY", "NINETY"]
_SCALES = [(10**9, "BILLION"), (10**6, "MILLION"), (1000, "THOUSAND"), (100, "HUNDRED")]


def __n2w(n):
    """ Convert a non-negative integer to its English words representation (uppercase). """
    if n < 20:
        return _ONES[n]
    if n < 100:
        return _TENS[n // 10] + ("" if (r := n % 10) == 0 else " " + _ONES[r])
    for s, w in _SCALES:
        if n >= s:
            return __n2w(n // s) + " " + w + ("" if (r := n % s) == 0 else " " + __n2w(r))


def __build_grids(number, key, alphabet, grid_size, replace_char):
    """ Build the substitution maps between the first grid (alphabet in columns) and the second grid (keyword or number
         in words, then the remaining letters, in rows). """
    # the first grid is filled in columns, hence position i in rows holds the letter at index (i % n) * n + i // n
    g1 = [alphabet[(i % grid_size) * grid_size + i // grid_size] for i in range(grid_size ** 2)]
    g2 = keyed_square(key or __n2w(number), alphabet, replace_char)
    return dict(zip(g1, g2)), dict(zip(g2, g1))


def __set_params(numkey, key, grid_size, replace_char):
    numkey = str(numkey or "")
    if not re.match(r"^\d+(?:,\d+)*$", numkey):
        raise LookupError("Bad parameter for encoding 'bazeries': numeric key must be given")
    # group sizes are the digits of the key or, when separated by commas, the given numbers ; null sizes are ignored
    sizes = [s for s in map(int, numkey.split(",") if "," in numkey else numkey) if s > 0]
    if len(sizes) == 0:
        raise LookupError("Bad parameter for encoding 'bazeries': numeric key must hold at least one non-null group size")
    gs, rc, alphabet = square_params("bazeries", grid_size, replace_char)
    return sizes, __build_grids(int(numkey.replace(",", "")), key, alphabet, gs, rc), gs, rc


def __bazeries(decode=False):
    def _wrapper(numkey=None, key=None, grid_size=None, replace_char=None):
        # bad parameters are only reported when coding, as the lookup of the bare codec name must succeed (e.g. when
        #  listing the encodings)
        try:
            params = __set_params(numkey, key, grid_size, replace_char)
        except LookupError as e:
            params = e
        def _code(text, errors="strict"):
            if isinstance(params, LookupError):
                raise params
            sizes, maps, gsize, rchar = params
            smap = maps[decode]
            text = ensure_str(text)
            # only letters of the grid are transposed and substituted ; other characters and the case are kept in place
            slots, letters = [], []
            for i, c in enumerate(text):
                u = c.upper()
                if rchar and u == rchar[0]:
                    u = rchar[1]
                if u in smap:
                    slots.append(i)
                    letters.append(u)
            # reversing the groups is its own inverse and commutes with the substitution, hence the same code decodes
            result, i, j = list(text), 0, 0
            while i < len(letters):
                group = letters[i:i+sizes[j % len(sizes)]]
                for k, c in enumerate(group[::-1]):
                    pos, c = slots[i + k], smap[c]
                    # with a 6x6 grid, a letter may be substituted by a digit, which cannot hold its case
                    result[pos] = c.lower() if gsize == 5 and text[pos].islower() else c
                i += len(group)
                j += 1
            return (r := "".join(result)), len(r)
        return _code
    return _wrapper


add("bazeries", __bazeries(), __bazeries(True),
    r"^bazeries(?:[-_]cipher)?(?:[-_](\d+(?:,\d+)*))?(?:[-_]([a-zA-Z]+))?(?:[-_]([56])(?:[-_]([a-zA-Z]{2}))?)?$",
    printables_rate=1., penalty=.1)
