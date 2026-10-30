# -*- coding: UTF-8 -*-
"""Coquelet Codec - Coquelet content encoding.

Coquelet is a Multi Frequency-Shift Keying (MFSK) radio teleprinter system developed by ACEC in Belgium in the 1950s,
 used by the armies and police services of Belgium, France, Algeria and other countries. Each character of the ITA-2
 (Baudot) code is sent as a sequence of two tones: the first one, out of the 8 tones of Group I, gives its bits 3 to 5,
 while the second one, out of the 4 tones of Group II, gives its bits 1 and 2. As with ITA-2, the LTR and FIG codes
 switch between the letters and the figures shifts.
- With Coquelet 13 (Mk 1), the tones of Group I range from 812 to 1022 Hz (every 30 Hz) and those of Group II from 1082
   to 1172 Hz, each tone lasting 75 ms ; a 1052 Hz tone is sent when idle.
- With Coquelet 8 (Mk 2), a synchronous system, the tones of Group I are 8 tones from 773 to 960 Hz (every 26.67 Hz),
   Group II being made of the last 4 of them, each tone lasting 37.5 or 75 ms ; tones 1 and 8 are sent alternately when
   idle.

The variant is given with the codec name (e.g. "coquelet-8") ; it defaults to Coquelet 13. Encoding gives the
 frequencies of the tones in Hz, separated by spaces (letters being uppercased and the letters shift being assumed at
 the start), while decoding ignores the idle tones of Coquelet 13 (the idle sequence of Coquelet 8 being read as "M",
 whose tones are the same).

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

References: https://www.cryptomuseum.com/ref/coquelet/index.htm (Coquelet 13)
            https://www.wavecom.ch/content/ext/DecoderOnlineHelp/worddocuments/coquelet8.htm (Coquelet 8)
"""
from ._ita2 import ita2_decode, ita2_encode
from ..__common__ import *


__examples__ = {
    'enc(coquelet-12|coquelet-mk3)': None,
    'enc(coquelet|coquelet13|coquelet-13|coquelet_mk1)': {'TEST': "872 1172 1022 1112 902 1112 872 1172"},
    'enc(coquelet8|coquelet-8|coquelet_mk2)': {'TEST': "826 960 960 907 853 907 826 960"},
    'enc(coquelet)': {'A1': "1022 1082 842 1082 932 1082", '1A': "842 1082 932 1082 812 1082 1022 1082",
                      'a\x00\n\r': "1022 1082 1022 1172 1022 1142 992 1172", '#': None},
    'dec(coquelet)': {'1052 872 1172 1052 1052 1022 1112': "TE", '872 1172 1022': None, '1082 872': None,
                      '872 1000': None},
    'dec(coquelet8)': {'826 960 960 907': "TE", '773 960 773 960': "MM", '960 773 960': None, '826 773': None},
    'enc-dec(coquelet|coquelet8)': ["", "HELLO WORLD", "COQUELET 13, MK 1 (1950'S): $5 + 3; 8?!",
                                    "LINE 1\r\nLINE 2\x07\x05"],
}
__guess__ = ["coquelet", "coquelet8"]


# frequencies of the tones of Group I by bits 3 to 5 of the codes (code >> 2) and of Group II by bits 1 and 2
#  (code & 3), that is, tones 8, 4, 7, 6, 3, 5, 2, 1 and 12, 10, 11, 9 of Crypto Museum's table for Coquelet 13, and
#  tones 8, 4, 7, 6, 3, 5, 2, 1 and 8, 6, 7, 5 of Wavecom's table for Coquelet 8 (with its rounded frequencies)
COQUELET8_TONES = [773, 800, 826, 853, 880, 907, 933, 960]
COQUELET_VARIANTS = {
    13: ([812 + 30 * (t - 1) for t in [8, 4, 7, 6, 3, 5, 2, 1]], [1082 + 30 * (t - 9) for t in [12, 10, 11, 9]], 1052),
    8:  ([COQUELET8_TONES[t - 1] for t in [8, 4, 7, 6, 3, 5, 2, 1]], [COQUELET8_TONES[t - 1] for t in [8, 6, 7, 5]],
         None),
}
COQUELET_NAMES = {'13': 13, 'mk1': 13, '8': 8, 'mk2': 8}


def _variant(variant):
    # a bad variant is only reported when coding, as the lookup of the bare codec name must succeed (e.g. when listing
    #  the encodings)
    v = COQUELET_NAMES.get(str(variant or 13).lower().replace("-", "").replace("_", ""))
    if v is None:
        raise LookupError("Bad parameter for encoding 'coquelet': variant must be 13 (Mk1) or 8 (Mk2)")
    g1, g2, idle = COQUELET_VARIANTS[v]
    return g1, g2, idle, {(str(g1[c >> 2]), str(g2[c & 3])): c for c in range(32)}


def coquelet_encode(variant=None):
    def encode(text, errors="strict"):
        g1, g2, _, _ = _variant(variant)
        codes = ita2_encode("coquelet", ensure_str(text), errors)
        return " ".join(c if isinstance(c, str) else f"{g1[c >> 2]} {g2[c & 3]}" for c in codes), len(text)
    return encode


def coquelet_decode(variant=None):
    def decode(text, errors="strict"):
        _, _, idle, pairs = _variant(variant)
        _h, r, shift = handle_error("coquelet", errors, decode=True, kind="tone"), "", "letters"
        tones = [(i, t) for i, t in enumerate(ensure_str(text).split()) if t != str(idle)]
        j = 0
        while j < len(tones):
            (i, t1), t2 = tones[j], tones[j+1][1] if j + 1 < len(tones) else None
            # a tone of Group I must be followed by a tone of Group II ; otherwise, skip the first tone
            if (t1, t2) not in pairs:
                r += _h(t1, i, r)
                j += 1
                continue
            c, shift = ita2_decode(pairs[t1, t2], shift)
            r, j = r + c, j + 2
        return r, len(text)
    return decode


add("coquelet", coquelet_encode, coquelet_decode, r"^coquelet(?:[-_]?(\d+|mk[-_]?\d))?$", examples=__examples__,
    guess=__guess__, printables_rate=1.)
