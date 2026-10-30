# -*- coding: UTF-8 -*-
"""Piccolo Codec - Piccolo content encoding.

Piccolo is a Multi Frequency-Shift Keying (MFSK) radio teleprinter system used by the British Diplomatic Wireless
 Service (DWS) since 1962, sending the characters of the ITA-2 (Baudot) code as audio tones:
- Piccolo I sends each code as one of 32 tones, from 460 Hz (code 0) to 770 Hz (code 31), every 10 Hz ;
- Piccolo II (aka Piccolo Mk 6) sends each code as a sequence of two tones of 50 ms, out of 6 tones from 460 to 560 Hz,
   every 20 Hz, the pairs giving 36 combinations, of which 4 are not used for characters (two for synchronisation, one
   for multiple identification and one not used at all) ;
- Piccolo III sends the same pairs as Piccolo II, with 6 tones from 1900 to 2100 Hz, every 40 Hz.
As with ITA-2, the LTR and FIG codes switch between the letters and the figures shifts.

The variant is given with the codec name (e.g. "piccolo-1" or "piccolo-iii") ; it defaults to Piccolo II. Encoding
 gives the frequencies of the tones in Hz, separated by spaces (letters being uppercased and the letters shift being
 assumed at the start), while decoding ignores the synchronisation and identification pairs.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://www.cryptomuseum.com/ref/piccolo/index.htm
"""
from ._ita2 import CODES, FIG, LTR, ita2_decode, ita2_encode
from ..__common__ import *


__examples__ = {
    'enc(piccolo-4|piccolo-iv|piccolo-mk12)': None,
    'enc(piccolo|piccolo2|piccolo-ii|piccolo_mk6)': {'TEST': "500 460 460 480 460 540 500 460"},
    'enc(piccolo1|piccolo-i)': {'TEST': "620 470 510 620"},
    'enc(piccolo3|piccolo-iii)': {'TEST': "1980 1900 1900 1940 1900 2060 1980 1900"},
    'enc(piccolo)': {'A1': "460 560 560 560 520 560", '1A': "560 560 520 560 540 560 460 560",
                     'a\x00\n\r': "460 560 460 460 460 500 480 460", '#': None},
    'dec(piccolo)': {'520 540 500 460 540 520 540 540 460 540': "TS", '500 460 460 480': "TE", '500 460 520 520': None,
                     '500 460 460': None, '500 470': None},
    'dec(piccolo1)': {'620 470 470 620': "TEET", '620 475': None},
    'enc-dec(piccolo|piccolo1|piccolo3)': ["", "HELLO WORLD", "PICCOLO II, MK 6 (1962'S): $5 + 3; 8?!",
                                          "LINE 1\r\nLINE 2\x07\x05"],
}
__guess__ = ["piccolo1", "piccolo2", "piccolo3"]


# ITA-2 characters by second tone (rows) and first tone (columns), from A (lowest) to F, as LTR ("<") and FIG (">")
#  for the shifts ; the pairs DE and ED are used for synchronisation, EE for multiple identification, and DD is not used
PICCOLO_MATRIX = ["\x00\rTICO", "EDZUKB", "\nRLPVG", " NH..M", "SFY..X", "AJWQ<>"]
PICCOLO_PAIRS = {c: (t1, t2) for t2, row in enumerate(PICCOLO_MATRIX) for t1, c in enumerate(
                 {'<': LTR, '>': FIG}.get(c, CODES['letters'].get(c)) for c in row) if c is not None}
PICCOLO_CODES = {pair: c for c, pair in PICCOLO_PAIRS.items()}
PICCOLO_SYNC = [(3, 4), (4, 3), (4, 4)]
# first frequency and step of the tones by variant
PICCOLO_TONES = {1: (460, 10), 2: (460, 20), 3: (1900, 40)}
PICCOLO_VARIANTS = {'1': 1, 'i': 1, '2': 2, 'ii': 2, 'mk6': 2, '3': 3, 'iii': 3}


def _variant(variant):
    # a bad variant is only reported when coding, as the lookup of the bare codec name must succeed (e.g. when listing
    #  the encodings)
    v = PICCOLO_VARIANTS.get(str(variant or 2).lower().replace("-", "").replace("_", ""))
    if v is None:
        raise LookupError("Bad parameter for encoding 'piccolo': variant must be 1 (I), 2 (II, Mk6) or 3 (III)")
    return v, *PICCOLO_TONES[v]


def piccolo_encode(variant=None):
    def encode(text, errors="strict"):
        v, f, step = _variant(variant)
        tones = []
        for c in ita2_encode("piccolo", ensure_str(text), errors):
            if isinstance(c, str):
                tones.append(c)
            else:
                tones.extend(str(f + step * t) for t in ([c] if v == 1 else PICCOLO_PAIRS[c]))
        return " ".join(tones), len(text)
    return encode


def piccolo_decode(variant=None):
    def decode(text, errors="strict"):
        v, f, step = _variant(variant)
        _h, r, shift = handle_error("piccolo", errors, decode=True, kind="tone"), "", "letters"
        tones, idx = ensure_str(text).split(), {str(f + step * t): t for t in range(32 if v == 1 else 6)}
        j = 0
        while j < len(tones):
            t1, t2 = idx.get(tones[j]), idx.get(tones[j+1]) if j + 1 < len(tones) else None
            if v == 1 and t1 is not None:
                code, j = t1, j + 1
            elif v > 1 and (t1, t2) in PICCOLO_CODES:
                code, j = PICCOLO_CODES[t1, t2], j + 2
            elif v > 1 and (t1, t2) in PICCOLO_SYNC:
                j += 2
                continue
            else:
                # skip the first tone of an unknown pair (or an unknown tone)
                r += _h(tones[j], j, r)
                j += 1
                continue
            c, shift = ita2_decode(code, shift)
            r += c
        return r, len(text)
    return decode


add("piccolo", piccolo_encode, piccolo_decode, r"^piccolo(?:[-_]?(\d|i{1,3}|iv|mk[-_]?\d+))?$", examples=__examples__,
    guess=__guess__, printables_rate=1.)
