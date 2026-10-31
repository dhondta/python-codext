# -*- coding: UTF-8 -*-
"""Four-square Cipher Codec - four-square content encoding.

The Four-square cipher is a symmetric encryption method using polygram substitution with bigrams (pairs of letters),
 invented by Felix Delastelle. It relies on four squares arranged in a 2x2 matrix: the upper-left and lower-right ones
 hold the alphabet in order, while the upper-right and lower-left ones are filled with two keywords. For each pair, the
 first letter is located in the upper-left square and the second one in the lower-right square ; they are replaced by
 the letters at the other corners of the rectangle they form, that is, the letter of the upper-right square in the row
 of the first letter, then the letter of the lower-left square in the row of the second letter.

The 5x5 squares (I and J sharing a cell by default) or the 6x6 squares (letters and digits) can be used, with the
 replaced pair of letters being configurable in the codec name. Whitespace is removed and a text with an odd number of
 letters is padded with an "X".

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Four-square_cipher
"""
from ._square import *
from ..__common__ import *


__examples__ = {
    'enc(foursquare)':                       None,
    'enc(foursquare-example)':               None,
    'enc(foursquare-example-keyword-6-ji)':  None,
    'enc(foursquare-example-keyword-5-jj)':  None,
    'enc(four-square-example-keyword-5-qk)': {'help me obi wan kenobi': "FYGMKYHOBXMFKKKIMD"},
    'dec(four_square-example-keyword-5-qk)': {'FYGMKYHOBXMFKKKIMD': "HELPMEOBIWANKENOBI"},
    'enc(foursquare_cipher-example-keyword)': {'Test!': None, 'TEST': "TWSP", 'TES': "TWRV",
                                               'JUNK': "FQNA", 'IUNK': "FQNA"},
    'dec(foursquare_cipher-example-keyword)': {'SAQ': None, 'SA?T': None},
    'enc(foursquare-example-keyword-5-xy)':  {'A': "MS", 'AY': "MS"},
    'enc(foursquare-secret-key-6)':          {'JUNK MAIL 42': "FUNFJKIG8X"},
    'enc-dec(foursquare-example-keyword)':   ["HELPMEOBIWANKENOBI", "ATTACKATDAWN"],
    'enc-dec(foursquare-secret-key-6)':      ["JUNKMAIL42", "HIDEGOLD2026"],
    'enc-dec(foursquare-example-keyword-5-wv)': ["ITISJUSTATESTAGAIN"],
}
__guess__ = []


def __foursquare(decode=False):
    def _wrapper(key1=None, key2=None, grid_size=None, replace_char=None):
        # bad parameters are only reported when coding, as the lookup of the bare codec name must succeed (e.g. when
        #  listing the encodings)
        try:
            if not key1 or not key2:
                raise LookupError("Bad parameter for encoding 'foursquare': two keywords must be given")
            n, rc, alphabet = square_params("foursquare", grid_size, replace_char)
        except LookupError as e:
            err = e
            def _code(text, errors="strict"):
                raise err
            return _code
        # plaintext squares (upper-left and lower-right) and ciphertext squares (upper-right and lower-left)
        sq1, sq2 = keyed_square(key1, alphabet, rc), keyed_square(key2, alphabet, rc)
        p, p1, p2 = [{c: divmod(i, n) for i, c in enumerate(sq)} for sq in (alphabet, sq1, sq2)]
        def _pair(a, b):
            if decode:
                (r1, c2), (r2, c1) = p1[a], p2[b]
                return alphabet[r1 * n + c1], alphabet[r2 * n + c2]
            (r1, c1), (r2, c2) = p[a], p[b]
            return sq1[r1 * n + c2], sq2[r2 * n + c1]
        return digraph_codec("foursquare", _pair, alphabet, rc, decode)
    return _wrapper


add("foursquare", __foursquare(), __foursquare(True),
    r"^four[-_]?square(?:[-_]cipher)?(?:[-_]([a-zA-Z]+))?(?:[-_]([a-zA-Z]+))?(?:[-_]([56])(?:[-_]([a-zA-Z]{2}))?)?$",
    printables_rate=1., penalty=.1)
