# -*- coding: UTF-8 -*-
"""Radio Codec - NATO/Military phonetic alphabet content encoding.

The NATO phonetic alphabet (or ICAO radiotelephony spelling alphabet), adopted in the 1950s, assigns a code word to each
 letter (Alpha, Bravo, Charlie, ...) so that it can be spelled unambiguously over radio. Each letter is replaced by its
 code word, the words being separated by spaces and the spaces of the text by "/".

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/NATO_phonetic_alphabet
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


add_map("radio", ENCMAP, sep=" ", ignore_case="both", printables_rate=1., expansion_factor=(5.5, .3),
        pattern=r"^(?:military|nato|radio)(?:(?:[-_]phonetic)?(?:[-_]alphabet)?)?$")

