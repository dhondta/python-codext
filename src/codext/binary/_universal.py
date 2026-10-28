# -*- coding: UTF-8 -*-
"""Universal codes - common functions for the Elias and Fibonacci codecs.

Universal codes write positive integers as self-delimiting codewords, hence concatenated without separator. The codecs
 relying on these functions encode each character of the text from its ordinal + 1 (as 0 cannot be encoded), the output
 being a string of bits, or, with the "-integers" variant, lists of integers (from 1) in decimal.
"""
from ..__common__ import *


__all__ = ["universal", "INTEGERS", "PATTERN_INTEGERS", "TEXTS"]


# examples shared by the codecs
INTEGERS = "1 2 3 4 5 6 7 8 9 10 255 256 65535 18446744073709551616"
TEXTS = ["", "\x00", "Hello, World!", "Caf\u00e9 \U0001f600", "@random{512,1024}"]
# suffix of the codec name patterns for the variant with lists of integers
PATTERN_INTEGERS = r"(?:[-_](int(?:egers?)?))?$"


def universal(name, enc, dec, decode=False):
    """ Make the encoding or decoding function of a universal code, given the functions that encode an
         integer and that decode the codeword starting at a given index of a string of bits. """
    def _wrapper(integers=""):
        def _code(text, errors="strict"):
            _h, r = handle_error(name, errors, decode=decode, kind="token" if integers and not decode else
                                 ["character", "bits"][decode]), []
            text = ensure_str(text)
            if decode:
                bits, i = "", 0
                for k, c in enumerate(text):
                    if c in "01":
                        bits += c
                    elif not c.isspace():
                        # a wrong character cannot be replaced in the bit stream, hence it is dropped
                        _h(c, k)
                # the index of the next codeword is None after an incomplete codeword, which cannot be decoded
                while i is not None and i < len(bits):
                    n, j = dec(bits, i)
                    if n is None or not integers and n > 0x110000:
                        r.append(_h(bits[i:j], i, ["", " "][bool(integers)].join(r)))
                    else:
                        # characters are encoded from their ordinal + 1, as 0 cannot be encoded
                        r.append(str(n) if integers else chr(n - 1))
                    i = j
                return (s := (" ".join(x for x in r if x != "") if integers else "".join(r))), len(s)
            if integers:
                for m in re.finditer(r"[^\s,]+", text):
                    t = m.group()
                    # only integers from 1 can be encoded
                    r.append(enc(int(t)) if re.match(r"^\+?\d+$", t) and int(t) > 0 else _h(t, m.start()))
            else:
                r = [enc(ord(c) + 1) for c in text]
            return (s := "".join(r)), len(s)
        return _code
    return _wrapper

