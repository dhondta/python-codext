# -*- coding: UTF-8 -*-
"""Radio Codec - NATO/Military phonetic alphabet content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


__examples__ = {
    'enc(radio|military-alphabet)':      {'test':   "Tango Echo Sierra Tango"},
    'enc(nato-alphabet|radio-phonetic)': {'string': "Sierra Tango Romeo India November Golf"},
}


ENCMAP = {
    'A': "Alpha", 'B': "Bravo", 'C': "Charlie", 'D': "Delta", 'E': "Echo", 'F': "Foxtrot", 'G': "Golf", 'H': "Hotel",
    'I': "India", 'J': "Juliett", 'K': "Kilo", 'L': "Lima", 'M': "Mike", 'N': "November", 'O': "Oscar", 'P': "Papa",
    'Q': "Quebec", 'R': "Romeo", 'S': "Sierra", 'T': "Tango", 'U': "Uniform", 'V': "Victor", 'W': "Whiskey",
    'X': "X-ray", 'Y': "Yankee", 'Z': "Zulu", ' ': "/",
}


add_map("radio", ENCMAP, sep=" ", ignore_case="both",
        pattern=r"^(?:military|nato|radio)(?:(?:[-_]phonetic)?(?:[-_]alphabet)?)?$", printables_rate=1.)

