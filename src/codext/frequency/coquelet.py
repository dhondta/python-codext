# -*- coding: UTF-8 -*-
"""Coquelet Codec - Coquelet content encoding.

Coquelet is a Multi Frequency-Shift Keying (MFSK) radio teleprinter system developed by ACEC in Belgium in the 1950s,
 used by the armies and police services of Belgium, France, Algeria and other countries. With Coquelet 13 (Mk 1), each
 character of the ITA-2 (Baudot) code is sent as a sequence of two tones of 75 ms: the first one, out of the 8 tones of
 Group I (812 to 1022 Hz, every 30 Hz), gives its bits 3 to 5, while the second one, out of the 4 tones of Group II
 (1082 to 1172 Hz), gives its bits 1 and 2. A 1052 Hz tone is sent when idle. As with ITA-2, the LTR and FIG codes
 switch between the letters and the figures shifts.

Encoding gives the frequencies of the tones in Hz, separated by spaces (letters being uppercased and the letters shift
 being assumed at the start), while decoding ignores idle tones.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://www.cryptomuseum.com/ref/coquelet/index.htm
"""
from ._ita2 import ita2_decode, ita2_encode
from ..__common__ import *


__examples__ = {
    'enc(coquelet|coquelet13|coquelet-13|coquelet_mk1)': {'TEST': "872 1172 1022 1112 902 1112 872 1172"},
    'enc(coquelet)': {'A1': "1022 1082 842 1082 932 1082", '1A': "842 1082 932 1082 812 1082 1022 1082",
                      'a\x00\n\r': "1022 1082 1022 1172 1022 1142 992 1172", '#': None},
    'dec(coquelet)': {'1052 872 1172 1052 1052 1022 1112': "TE", '872 1172 1022': None, '1082 872': None,
                      '872 1000': None},
    'enc-dec(coquelet)': ["", "HELLO WORLD", "COQUELET 13, MK 1 (1950'S): $5 + 3; 8?!", "LINE 1\r\nLINE 2\x07\x05"],
}
__guess__ = ["coquelet"]


# frequencies of the tones of Group I by bits 3 to 5 of the codes (code >> 2) and of Group II by bits 1 and 2
#  (code & 3), that is, tones 8, 4, 7, 6, 3, 5, 2, 1 and 12, 10, 11, 9 of Crypto Museum's table
COQUELET_GROUP1 = [812 + 30 * (t - 1) for t in [8, 4, 7, 6, 3, 5, 2, 1]]
COQUELET_GROUP2 = [1082 + 30 * (t - 9) for t in [12, 10, 11, 9]]
COQUELET_IDLE = 1052
COQUELET_PAIRS = {(str(COQUELET_GROUP1[c >> 2]), str(COQUELET_GROUP2[c & 3])): c for c in range(32)}


def coquelet_encode(text, errors="strict"):
    codes = ita2_encode("coquelet", ensure_str(text), errors)
    tones = [c if isinstance(c, str) else f"{COQUELET_GROUP1[c >> 2]} {COQUELET_GROUP2[c & 3]}" for c in codes]
    return " ".join(tones), len(text)


def coquelet_decode(text, errors="strict"):
    _h, r, shift = handle_error("coquelet", errors, decode=True, kind="tone"), "", "letters"
    tones = [(i, t) for i, t in enumerate(ensure_str(text).split()) if t != str(COQUELET_IDLE)]
    j = 0
    while j < len(tones):
        (i, t1), t2 = tones[j], tones[j+1][1] if j + 1 < len(tones) else None
        # a tone of Group I must be followed by a tone of Group II ; otherwise, skip the first tone
        if (t1, t2) not in COQUELET_PAIRS:
            r += _h(t1, i, r)
            j += 1
            continue
        c, shift = ita2_decode(COQUELET_PAIRS[t1, t2], shift)
        r, j = r + c, j + 2
    return r, len(text)


add("coquelet", coquelet_encode, coquelet_decode, r"^coquelet(?:[-_]?(?:13|mk[-_]?1))?$", examples=__examples__,
    guess=__guess__, printables_rate=1.)
