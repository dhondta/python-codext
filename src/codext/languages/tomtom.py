# -*- coding: UTF-8 -*-
"""Tom-Tom Codec - tom-tom content encoding.

The Tom-Tom code writes each letter as a short sequence of slashes and backslashes (e.g. "/" for A, "/\" for E), the
 letters being separated by spaces and the words by "|" ; the three symbols can be replaced in the codec name (e.g.
 "tom-tom-/01").

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://www.dcode.fr/tom-tom-code
"""
from ..__common__ import *


__examples__ = {
    'enc': {
        'this is a test': "\\\\/\\ /\\\\ /\\\\\\ \\/\\ | /\\\\\\ \\/\\ | / | \\\\/\\ /\\ \\/\\ \\\\/\\"
    }
}
__guess__ = ["tom-tom", "tom-tom/_.", "tom-tom-/01", "tom-tom-01", "tom-tom-/ab", "tom-tom-ab", "tom-tom-/AB",
             "tom-tom-AB"]


ENCMAP = {
    # letters
    'A': "/", 'B': "//", 'C': "///", 'D': "////", 'E': "/\\", 'F': "//\\", 'G': "///\\", 'H': "/\\\\",  'I': "/\\\\\\",
    'J': "\\/", 'K': "\\\\/", 'L': "\\\\\\/", 'M': "\\//", 'N': "\\///", 'O': "/\\/", 'P': "//\\/", 'Q': "/\\\\/",
    'R': "/\\//", 'S': "\\/\\", 'T': "\\\\/\\", 'U': "\\//\\", 'V': "\\/\\\\", 'W': "//\\\\", 'X': "\\\\//",
    'Y': "\\/\\/", 'Z': "/\\/\\",
    # word separator
    ' ' : "|",
}


add_map("tom-tom", ENCMAP, ".", " ", ignore_case="both", pattern=r"^tom-?tom([-_]?.{3})?$", printables_rate=1.,
        expansion_factor=(3.8, .2))

