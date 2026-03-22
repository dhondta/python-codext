# -*- coding: UTF-8 -*-
"""Navajo Codec - Navajo code content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


__examples__ = {'enc-dec(navajo)': ["this is a test", "THIS\nIS\nA\nTEST"]}


# source: https://www.history.navy.mil/research/library/online-reading-room/title-list-alphabetically/n/navajo-code-talker-dictionary.html
ENCMAP = {
    'A': ["WOL-LA-CHEE", "BE-LA-SANA", "TSE-NILL"], 'B': ["NA-HASH-CHID", "SHUSH", "TOISH-JEH"],
    'C': ["MOASI", "TLA-GIN", "BA-GOSHI"], 'D': ["BE", "CHINDI", "LHA-CHA-EH"], 'E': ["AH-JAH", "DZEH", "AH-NAH"],
    'F': ["CHUO", "TSA-E-DONIN-EE", "MA-E"], 'G': ["AH-TAD", "KLIZZIE", "JEHA"], 'H': ["TSE-GAH", "CHA", "LIN"],
    'I': ["TKIN", "YEH-HES", "A-CHI"], 'J': ["TKELE-CHO-G", "AH-YA-TSINNE", "YIL-DOI"],
    'K': ["JAD-HO-LONI", "BA-AH-NE-DI-TININ", "KLIZZIE-YAZZIE"], 'L': ["DIBEH-YAZZIE", "AH-JAD", "NASH-DOIE-TSO"],
    'M': ["TSIN-TLITI", "BE-TAS-TNI", "NA-AS-TSO-SI"], 'N': ["TSAH", "A-CHIN"],
    'O': ["A-KHA", "TLO-CHIN", "NE-AHS-JAH"], 'P': ["CLA-GI-AIH", "BI-SO-DIH", "NE-ZHONI"], 'Q': "CA-YEILTH",
    'R': ["GAH", "DAH-NES-TSA", "AH-LOSZ"], 'S': ["DIBEH", "KLESH"], 'T': ["D-AH", "A-WOH", "THAN-ZIE"],
    'U': ["SHI-DA", "NO-DA-IH"], 'V': "A-KEH-DI-GLINI", 'W': "GLOE-IH", 'X': "AL-NA-AS-DZOH", 'Y': "TSAH-AS-ZIH",
    'Z': "BESH-DO-TLIZ",
    ' ': "-", '\n': "\n",
    '0': "0", '1': "1", '2': "2", '3': "3", '4': "4", '5': "5", '6': "6", '7': "7", '8': "8", '9': "9",
}


add_map("navajo", ENCMAP, ignore_case="both", sep=" ", pattern=r"^navajo$", printables_rate=1.,
        expansion_factor=(6.2, .8))

