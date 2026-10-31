# -*- coding: UTF-8 -*-
"""X-Y Codec - binary content encoding with two symbols.

The X-Y encoding (also called "X and Y") writes each byte as its 8 bits, with one symbol for 0 and another for 1,
 "x" and "y" by default. Two other symbols can be given in the codec name, e.g. "xy-AB" (A for 0 and B for 1) or
 "xy-01" (hence the plain binary of the text).

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://github.com/Ciphey/Ciphey/blob/master/ciphey/basemods/Crackers/xandy.py (X-Y cracker)
"""
from ..__common__ import *


__examples__ = {
    'enc(xy)':      {'test': "xyyyxyxxxyyxxyxyxyyyxxyyxyyyxyxx"},
    'enc(xy-AB)':   {'test': "ABBBABAAABBAABABABBBAABBABBBABAA"},
    'enc(x_y_01)':  {'test': "01110100011001010111001101110100"},
    'dec(xy)':      {'xyyyxyxx': "t", 'xyyyxyxz': None},
    'enc-dec(xy|x-y|x_y|xy-AB|xy_zo)': ["", "this is a test", "Hello, World! 123", "\xe9t\xe9 \xff"],
}
__guess__ = ["xy"]


add_map("xy", {'0': "x", '1': "y"}, intype="bin", pattern=r"^x[-_]?y(|[-_].{2})$", entropy=1., printables_rate=1.,
        expansion_factor=8.)
