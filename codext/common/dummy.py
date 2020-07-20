# -*- coding: UTF-8 -*-
"""Dummy Codecs - simple string manipulations.

These are dummy codecs for manipulating strings, for use with other codecs in encoding/decoding chains.

These codecs:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ..__common__ import add


capitalize = lambda i, e="strict": (i.capitalize(), len(i))
uncapitalize = lambda i, e="strict": (i[0].lower() + i[1:] if len(i) > 0 else "", len(i))
add("capitalize", capitalize, uncapitalize)

reverse = lambda i, e="strict": (i[::-1], len(i))
add("reverse", reverse, reverse)

word_reverse = lambda i, e="strict": (" ".join(w[::-1] for w in i.split()), len(i))
add("reverse-words", word_reverse, word_reverse, r"^reverse[-_]words$")

swapcase = lambda i, e="strict": (i.swapcase(), len(i))
add("swapcase", swapcase, swapcase, r"^swap(?:case)?$")

title = lambda i, e="strict": (i.title(), len(i))
untitle = lambda i, e="strict": (" ".join(w[0].lower() + w[1:] if len(w) > 0 else "" for w in i.split()), len(i))
add("title", title, untitle)

lowercase = lambda i, e="strict": (i.lower(), len(i))
uppercase = lambda i, e="strict": (i.upper(), len(i))
add("uppercase", uppercase, lowercase, r"^upper(?:case)?$")
add("lowercase", lowercase, uppercase, r"^lower(?:case)?$")

