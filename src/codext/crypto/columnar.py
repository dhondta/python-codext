# -*- coding: UTF-8 -*-
"""Columnar Transposition Cipher Codec - columnar content encoding.

The text is written in rows under a keyword, then read column by column, in the alphabetical order of the keyword
 letters (from left to right for repeated letters). The last row may be incomplete (irregular columnar transposition) ;
 a regular transposition is obtained by padding the text beforehand. With a second keyword, the result is transposed
 again (double transposition). Every character is transposed, including whitespaces and punctuation.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Transposition_cipher#Columnar_transposition
"""
from ..__common__ import *


__examples__ = {
    'enc(columnar-zebras|columnar_transposition-zebras|columnar-cipher-zebras)': {
        'WEAREDISCOVEREDFLEEATONCE':      "EVLNACDTESEAROFODEECWIREE",
        'WEAREDISCOVEREDFLEEATONCEQKJEU': "EVLNEACDTKESEAQROFOJDEECUWIREE"},
    'dec(columnar-zebras)':               {'EVLNACDTESEAROFODEECWIREE': "WEAREDISCOVEREDFLEEATONCE"},
    'enc(columnar-zebras-stripe)':        {'WEAREDISCOVEREDFLEEATONCE': "CAEENSOIAEDRLEFWEDREEVTOC"},
    'dec(columnar_transposition-zebras-stripe)': {'CAEENSOIAEDRLEFWEDREEVTOC': "WEAREDISCOVEREDFLEEATONCE"},
    'enc(columnar-3142)':                 {'abcdefgh': "bfdhaecg"},
    'enc(columnar|columnar-cipher|columnar_transposition)': None,
    'dec(columnar)':                      None,
    'enc-dec(columnar-key|columnar-Secret|columnar-a|columnar-1918|columnar-zebras-stripe)': [
        "", "a", "Hello, World!", "We are discovered, flee at once!", "@random{512,1024,2048}"],
}
__guess__ = []


def __orders(key1, key2):
    # a missing key is only reported when coding, as the lookup of the bare codec name must succeed (e.g. when listing
    #  the encodings)
    if not key1:
        return LookupError("Bad parameter for encoding 'columnar': a keyword is required")
    return [__order(k) for k in (key1, key2) if k]


def __order(key):
    """ Columns are read in the alphabetical order of the keyword letters, from left to right for repeated letters. """
    key = str(key).upper()
    return sorted(range(len(key)), key=lambda i: (key[i], i))


def columnar_encode(key1=None, key2=None):
    orders = __orders(key1, key2)
    def encode(text, errors="strict"):
        if isinstance(orders, LookupError):
            raise orders
        text = ensure_str(text)
        for order in orders:
            text = "".join(text[j::len(order)] for j in order)
        return text, len(text)
    return encode


def columnar_decode(key1=None, key2=None):
    orders = __orders(key1, key2)
    def decode(text, errors="strict"):
        if isinstance(orders, LookupError):
            raise orders
        text = ensure_str(text)
        for order in orders[::-1]:
            # columns lengths, considering the last row may be incomplete
            n, l = len(order), len(text)
            lengths, cols, i = [l // n + (j < l % n) for j in range(n)], [""] * n, 0
            for j in order:
                cols[j], i = text[i:i+lengths[j]], i + lengths[j]
            text = "".join(cols[j][k] for k in range(max(lengths)) for j in range(n) if k < lengths[j])
        return text, len(text)
    return decode


add("columnar", columnar_encode, columnar_decode,
    r"^columnar(?:[-_]transposition)?(?:[-_]cipher)?(?:[-_]([a-zA-Z0-9]+))?(?:[-_]([a-zA-Z0-9]+))?$", penalty=.1)
