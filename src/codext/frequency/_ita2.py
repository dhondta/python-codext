# -*- coding: UTF-8 -*-
"""ITA-2 code shared by the frequency codecs, which send its 5-bit codes as audio tones.

The codes are numbered with bit 1 (the first one sent) as the least significant bit. As 32 codes are not enough, the LTR
 and FIG codes switch between the letters and the figures shifts.
"""
from ..__common__ import handle_error


LTR, FIG = 31, 27
# characters by code, with the figures of ITA-2 except ";" instead of "=" (as given by Crypto Museum for Coquelet) ;
#  None stands for the shift codes
CHARS = {shift: [None if c == "\xff" else c for c in chars] for shift, chars in [
    ('letters', "\x00E\nA SIU\rDRJNFCKTZLWHYPQOBG\xffMXV\xff"),
    ('figures', "\x003\n- '87\r\x054\x07,!:(5+)2$6019?&\xff./;\xff"),
]}
CODES = {shift: {c: i for i, c in enumerate(chars) if c is not None} for shift, chars in CHARS.items()}


def ita2_encode(ename, text, errors="strict"):
    """ Codes of the text (uppercased), with the shift codes inserted when needed, the letters shift being assumed at
         the start ; an unsupported character is encoded as "?" when replaced, or kept as a string when left as is. """
    _h, codes, shift = handle_error(ename, errors), [], "letters"
    for i, c in enumerate(text.upper()):
        if c not in CODES['letters'] and c not in CODES['figures']:
            if (c := _h(c, i)) != "?":
                codes.extend([c] if c else [])
                continue
        if c not in CODES[shift]:
            shift = ["letters", "figures"][shift == "letters"]
            codes.append(FIG if shift == "figures" else LTR)
        codes.append(CODES[shift][c])
    return codes


def ita2_decode(code, shift):
    """ Character of a code in the given shift (empty for a shift code), and the resulting shift. """
    if code in (LTR, FIG):
        return "", ["letters", "figures"][code == FIG]
    return CHARS[shift][code], shift
