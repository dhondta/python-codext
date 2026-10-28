# -*- coding: UTF-8 -*-
"""Two-square Cipher Codec - two-square content encoding.

The Two-square cipher (or Double Playfair) is a symmetric encryption method using polygram substitution with bigrams
 (pairs of letters), invented by Charles Wheatstone. It relies on two squares filled with two keywords, placed one above
 the other (vertical, by default) or side by side (horizontal). For each pair, the first letter is located in the first
 square (upper or left) and the second one in the second square (lower or right) ; they are replaced by the letters at
 the other corners of the rectangle they form:
- vertical: the letter of the upper square in the row of the first letter, then the letter of the lower square in the
   row of the second letter ; a pair whose letters are in the same column is left unchanged
- horizontal: the letter of the right square in the row of the first letter, then the letter of the left square in the
   row of the second letter ; a pair whose letters are in the same row is reversed

The 5x5 squares (I and J sharing a cell by default) or the 6x6 squares (letters and digits) can be used, with the
 orientation ("h" or "v") and the replaced pair of letters being configurable in the codec name. Whitespace is removed
 and a text with an odd number of letters is padded with an "X".

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Two-square_cipher
           https://www.dcode.fr/two-square-cipher
"""
from ._square import *
from ..__common__ import *


__examples__ = {
    'enc(twosquare)':                             None,
    'enc(twosquare-example)':                     None,
    'enc(twosquare-example-keyword-6-ji)':        None,
    'enc(twosquare-example-keyword-v-5-jj)':      None,
    'enc(two-square-example-keyword-5-qk)':       {'help me obi wan kenobi': "HEDLXWSDJYANHOTKDG"},
    'dec(two_square-example-keyword-v-5-qk)':     {'HEDLXWSDJYANHOTKDG': "HELPMEOBIWANKENOBI"},
    'enc(twosquare_cipher-example-keyword)':      {'help me obi wan kenobi': "HECMXWSRKYXPHWNODG", 'Test!': None},
    'dec(double-playfair-example-keyword)':       {'HECMX': None, 'HE?C': None},
    'enc(twosquare-key-word-h)':                  {'DCODEZ': "CDLBAV", 'DCODE': "CDLBRV"},
    'dec(twosquare-key-word-horizontal)':         {'CDLBAV': "DCODEZ"},
    'enc(twosquare-secret-key-6)':                {'JUNK MAIL 42': "MRJBMABQ8X"},
    'enc-dec(twosquare-example-keyword)':         ["HELPMEOBIWANKENOBI", "ATTACKATDAWN"],
    'enc-dec(twosquare-example-keyword-h)':       ["HELPMEOBIWANKENOBI", "ATTACKATDAWN"],
    'enc-dec(twosquare-secret-key-vertical-6)':   ["JUNKMAIL42", "HIDEGOLD2026"],
    'enc-dec(twosquare-secret-key-h-6)':          ["JUNKMAIL42", "HIDEGOLD2026"],
    'enc-dec(double_playfair-example-keyword-5-wv)': ["ITISJUSTATESTAGAIN"],
}
__guess__ = []


def __twosquare(decode=False):
    def _wrapper(key1=None, key2=None, orientation=None, grid_size=None, replace_char=None):
        # bad parameters are only reported when coding, as the lookup of the bare codec name must succeed (e.g. when
        #  listing the encodings)
        try:
            if not key1 or not key2:
                raise LookupError("Bad parameter for encoding 'twosquare': two keywords must be given")
            n, rc, alphabet = square_params("twosquare", grid_size, replace_char)
        except LookupError as e:
            err = e
            def _code(text, errors="strict"):
                raise err
            return _code
        sq1, sq2 = keyed_square(key1, alphabet, rc), keyed_square(key2, alphabet, rc)
        p1, p2 = [{c: divmod(i, n) for i, c in enumerate(sq)} for sq in (sq1, sq2)]
        h = (orientation or "v")[0] == "h"
        def _pair(a, b):
            # the vertical variant is its own inverse ; with the horizontal one, the ciphertext pair starts with the
            #  letter of the right square, hence decoding takes its letters from the right square, then the left one
            if h and decode:
                (r1, c2), (r2, c1) = p2[a], p1[b]
                return sq1[r1 * n + c1], sq2[r2 * n + c2]
            (r1, c1), (r2, c2) = p1[a], p2[b]
            return (sq2[r1 * n + c2], sq1[r2 * n + c1]) if h else (sq1[r1 * n + c2], sq2[r2 * n + c1])
        return digraph_codec("twosquare", _pair, alphabet, rc, decode)
    return _wrapper


add("twosquare", __twosquare(), __twosquare(True),
    r"^(?:two[-_]?square|double[-_]playfair)(?:[-_]cipher)?(?:[-_]([a-zA-Z]+))?(?:[-_]([a-zA-Z]+))?"
    r"(?:[-_](h|v|horizontal|vertical))?(?:[-_]([56])(?:[-_]([a-zA-Z]{2}))?)?$", printables_rate=1., penalty=.1)
