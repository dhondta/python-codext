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


# frequencies of the tones 1 to 8 (Group I) and 9 to 12 (Group II)
TONES = [812 + 30 * i for i in range(8)] + [1082 + 30 * i for i in range(4)]
IDLE = 1052
# characters by (Group II tone - 9) * 8 + (Group I tone - 1), the first two codes being the LTR and FIG shifts
CHARS = {
    'letters': [None, None] + list("WUQKJAXBZSYFDEVGLIPCR\nMOT HN\r\x00"),
    'figures': [None, None] + list("271(\x07-/?+'6!\x053;&)80:4\n.95 $,\r\x00"),
}
CODES = {shift: {c: i for i, c in enumerate(chars) if c is not None} for shift, chars in CHARS.items()}


def coquelet_encode(text, errors="strict"):
    _h, tones, shift = handle_error("coquelet", errors), [], "letters"
    for i, c in enumerate(ensure_str(text).upper()):
        if c not in CODES['letters'] and c not in CODES['figures']:
            # a replaced character is encoded as "?", while a left one is kept as is in the output
            if (c := _h(c, i)) != "?":
                tones.extend([c] if c else [])
                continue
        if c not in CODES[shift]:
            shift = ["letters", "figures"][shift == "letters"]
            tones.append(shift == "figures")
        tones.append(CODES[shift][c])
    return " ".join(t if isinstance(t, str) else f"{TONES[t % 8]} {TONES[8 + t // 8]}" for t in tones), len(text)


def coquelet_decode(text, errors="strict"):
    _h, r, shift = handle_error("coquelet", errors, decode=True, kind="tone"), "", "letters"
    tones = [(i, t) for i, t in enumerate(ensure_str(text).split()) if t != str(IDLE)]
    idx = {str(f): n for n, f in enumerate(TONES)}
    j = 0
    while j < len(tones):
        (i, t1), t2 = tones[j], tones[j+1][1] if j + 1 < len(tones) else None
        # a tone of Group I must be followed by a tone of Group II ; otherwise, skip the first tone
        if idx.get(t1, 8) >= 8 or idx.get(t2, 0) < 8:
            r += _h(t1, i, r)
            j += 1
            continue
        n, j = (idx[t2] - 8) * 8 + idx[t1], j + 2
        if n < 2:
            shift = ["letters", "figures"][n]
        else:
            r += CHARS[shift][n]
    return r, len(text)


add("coquelet", coquelet_encode, coquelet_decode, r"^coquelet(?:[-_]?(?:13|mk[-_]?1))?$", examples=__examples__,
    guess=__guess__, printables_rate=1.)
