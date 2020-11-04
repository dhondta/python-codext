# -*- coding: UTF-8 -*-
"""Tom-Tom Codec - tom-tom content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
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


add_map("tom-tom", ENCMAP, ".", " ", ignore_case="both", pattern=r"^tom-?tom([-_]?.{3})?$")

