# -*- coding: UTF-8 -*-
"""Dummy Codecs - simple string manipulations.

These are dummy codecs for manipulating strings, for use with other codecs in encoding/decoding chains.

These codecs:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import *


capitalize = lambda i, e="strict": (i.capitalize(), len(i))
add("capitalize", capitalize, capitalize)

lowercase = lambda i, e="strict": (i.lower(), len(i))
add("lowercase", lowercase, lowercase, r"^lower(?:case)?$")

reverse = lambda i, e="strict": (i[::-1], len(i))
add("reverse", reverse, reverse)

swapcase = lambda i, e="strict": (i.swapcase(), len(i))
add("swapcase", swapcase, swapcase, r"^swap(?:case)?$")

title = lambda i, e="strict": (i.title(), len(i))
add("title", title, title)

uppercase = lambda i, e="strict": (i.upper(), len(i))
add("uppercase", uppercase, uppercase, r"^upper(?:case)?$")
