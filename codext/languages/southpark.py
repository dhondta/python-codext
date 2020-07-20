# -*- coding: UTF-8 -*-
"""Southpark Codec - Kenny's language content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


__examples1__ = {
    'enc_dec(kenny|southpark)': ["This is a Test"],
    'enc_dec(kenny_123456|southpark-ABCDEF)': ["This is a Test"],
}
__examples2__ = {
    'enc(southpark-icase|kenny_icase)': {'this is a test': "FMPMFPMFFFMMFFFMFFFMMFFFMMMFFFFMPMPPFMMFMP"},
    'enc(southpark_icase-123)':         {'this is a test': "123213211122111211122111222111123233122123"},
}


ENCMAP1 = {
    'a': "mmm", 'b': "mmp", 'c': "mmf", 'd': "mpm", 'e': "mpp", 'f': "mpf", 'g': "mfm", 'h': "mfp", 'i': "mff",
    'j': "pmm", 'k': "pmp", 'l': "pmf", 'm': "ppm", 'n': "ppp", 'o': "ppf", 'p': "pfm", 'q': "pfp", 'r': "pff",
    's': "fmm", 't': "fmp", 'u': "fmf", 'v': "fpm", 'w': "fpp", 'x': "fpf", 'y': "ffm", 'z': "ffp",
    'A': "Mmm", 'B': "Mmp", 'C': "Mmf", 'D': "Mpm", 'E': "Mpp", 'F': "Mpf", 'G': "Mfm", 'H': "Mfp", 'I': "Mff",
    'J': "Pmm", 'K': "Pmp", 'L': "Pmf", 'M': "Ppm", 'N': "Ppp", 'O': "Ppf", 'P': "Pfm", 'Q': "Pfp", 'R': "Pff",
    'S': "Fmm", 'T': "Fmp", 'U': "Fmf", 'V': "Fpm", 'W': "Fpp", 'X': "Fpf", 'Y': "Ffm", 'Z': "Ffp",
    ' ': ["fff", "Fff"],
}
ENCMAP2 = {
    'a': "MMM", 'b': "MMP", 'c': "MMF", 'd': "MPM", 'e': "MPP", 'f': "MPF", 'g': "MFM", 'h': "MFP", 'i': "MFF",
    'j': "PMM", 'k': "PMP", 'l': "PMF", 'm': "PPM", 'n': "PPP", 'o': "PPF", 'p': "PFM", 'q': "PFP", 'r': "PFF",
    's': "FMM", 't': "FMP", 'u': "FMF", 'v': "FPM", 'w': "FPP", 'x': "FPF", 'y': "FFM", 'z': "FFP", ' ': "FFF",
}


add_map("southpark", ENCMAP1, pattern=r"^(?:kenny|southpark)([-_].{6})?$", examples=__examples1__)
add_map("southpark-icase", ENCMAP2, ignore_case="both", pattern=r"^(?:kenny|southpark)[-_]icase([-_].{3})?$",
        examples=__examples2__)

