# -*- coding: UTF-8 -*-
"""Rick Astley Codec - Rick Astley's song content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


__examples__ = {
    'enc(rick|rick-astley)': {'this is a test': "TELL LET You gonna + You gonna + NEVER + TELL UP gonna TELL"},
}


# inspired from: https://github.com/moongazer07/rick-cipher
ENCMAP = {
    'A': "NEVER", 'B': "GONNA", 'C': "GIVE", 'D': "YOU", 'E': "UP", 'F': "Never", 'G': "Gonna", 'H': "LET", 'I': "You",
    'J': "DOWN", 'K': "NEver", 'L': "GOnna", 'M': "TURN", 'N': "AROUND", 'O': "AND", 'P': ["DESERT", "DESSERT"],
    'Q': "YOu", 'R': "NEVer", 'S': "gonna", 'T': "TELL", 'U': "A", 'V': "LIE", 'W': "and", 'X': "HURT", 'Y': "you",
    'Z': "rick", ' ': "+", '.': ".", '\n': "\n",
    '0': "0", '1': "1", '2': "2", '3': "3", '4': "4", '5': "5", '6': "6", '7': "7", '8': "8", '9': "9",
    '': "astley", # silent this token for decoding ("rick astley" causes an issue with the separator " ")
}


add_map("rick", ENCMAP, "?", " ", ignore_case="encode", pattern=r"^rick(?:[-_]astley)?(?:[-_]cipher)?$",
        printables_rate=1.)

