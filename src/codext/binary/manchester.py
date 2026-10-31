# -*- coding: UTF-8 -*-
"""Manchester Codec - Manchester content encoding.

Manchester code, from the University of Manchester where it was used for storing data on the Manchester Mark 1's
 magnetic drum, is a line code that guarantees a transition in the middle of each bit period (hence a self-clocking
 signal): each bit is written with two bits, as the XOR of the bit with the clock. By default, the convention of G. E.
 Thomas is used (1 is written 10 and 0 is written 01), while the inverted variant ("ethernet", "ieee802.4") uses the
 opposite convention of IEEE 802.3 (1 is written 01 and 0 is written 10). Each input byte thus gives two output bytes.

Differential Manchester code also has a transition in the middle of each bit period, but writes the bits as the
 presence or absence of a transition at the start of their period, hence it does not depend on the polarity of the
 signal: by default, 0 is written with a transition at the start and 1 without (as with IEEE 802.5, Token Ring), while
 the inverted variant writes 1 with a transition and 0 without. The level starts low ; with a non-strict errors
 handling, decoding ignores the missing transitions in the middle of the periods and a trailing byte.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Manchester_code
"""
from ..__common__ import *


__examples1__ = {'enc(manchester)': {'This is a test!': "fei\x95i\x96jZYUi\x96jZYUiVYUjeifjZjeYV"}}
__examples2__ = {
    'enc(manchester-inverted|ethernet|ieee802.4)': {
        'This is a test!': "\x99\x9a\x96j\x96i\x95\xa5\xa6\xaa\x96i\x95\xa5\xa6\xaa\x96\xa9\xa6\xaa\x95\x9a\x96\x99"
                           "\x95\xa5\x95\x9a\xa6\xa9",
    },
}

__examples3__ = {
    'enc(differential-manchester|diff-manchester|ieee802.5)': {'@': "\x95U", 'A': "\x95V"},
    'dec(differential-manchester)': {'\x95U': "@", '\x00\x00': None, '\x95': None},
    'enc-dec(differential-manchester)': ["", "@random{512}"],
}
__examples4__ = {
    'enc(differential-manchester-inverted|diff_manchester_inverted)': {'@': "Y\x99", 'A': "Y\x9a"},
    'enc-dec(differential-manchester-inverted)': ["", "@random{512}"],
}


def manchester_encode(clock):
    def encode(text, errors="strict"):
        r = ""
        for c in text:
            bin_c = bin(ord(c))[2:].zfill(8)
            for i in range(0, 8, 4):
                r += chr(int("".join(2*bit for bit in bin_c[i:i+4]), 2) ^ clock)
        return r, len(b(text))
    return encode


def manchester_decode(clock):
    def decode(text, errors="strict"):
        r, bits = "", ""
        for c in text:
            bin_c = bin(ord(c) ^ clock)[2:].zfill(8)
            bits += "".join(bin_c[i] for i in range(0, len(bin_c), 2))
            if len(bits) == 8:
                r += chr(int(bits, 2))
                bits = ""
        return r, len(b(text))
    return decode


def _differential(transition, decode=False):
    """ Differential Manchester encoding or decoding function, given the bit written with a transition at the start of
         its period. """
    ename = "differential-manchester" + "-inverted" * transition
    def _code(text, errors="strict"):
        data, level, r = b(ensure_str(text)), 0, []
        if not decode:
            for x in data:
                y = 0
                for i in range(7, -1, -1):
                    level ^= (x >> i & 1) == transition
                    y, level = y << 2 | level << 1 | level ^ 1, level ^ 1
                r.extend(y.to_bytes(2, "big"))
            return bytes(r).decode("latin-1"), len(text)
        _h = handle_error(ename, errors, decode=True, kind="half-bits", item="bit")
        if len(data) % 2:
            _h(f"{data[-1]:08b}", 8 * len(data) - 8)
        for j in range(0, len(data) - 1, 2):
            v, y = data[j] << 8 | data[j+1], 0
            for i in range(7, -1, -1):
                h1, h2 = v >> 2 * i + 1 & 1, v >> 2 * i & 1
                # each period must have a transition in its middle
                if h1 == h2:
                    _h(f"{h1}{h2}", 8 * j + 14 - 2 * i)
                y, level = y << 1 | (transition if h1 != level else 1 - transition), h2
            r.append(y)
        # the decoded data is given as bytes (then as text if it was text)
        return bytes(r), len(text)
    return _code


add("manchester", manchester_encode(0x55), manchester_decode(0x55), examples=__examples1__, printables_rate=.25,
    entropy=lambda e: .17616*e+2.56229)
add("manchester-inverted", manchester_encode(0xaa), manchester_decode(0xaa), examples=__examples2__,
    pattern=r"^(?:manchester-inverted|ethernet|ieee802\.4)$", entropy=lambda e: .17616*e+2.56229)
add("differential-manchester", _differential(0), _differential(0, True), examples=__examples3__,
    pattern=r"^diff(?:erential)?[-_]manchester$|^ieee802\.5$")
add("differential-manchester-inverted", _differential(1), _differential(1, True), examples=__examples4__,
    pattern=r"^diff(?:erential)?[-_]manchester[-_]inverted$")
