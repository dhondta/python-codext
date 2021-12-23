# -*- coding: UTF-8 -*-
"""Dummy Codecs - simple string manipulations.

These are dummy codecs for manipulating strings, for use with other codecs in encoding/decoding chains.

These codecs:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
import re

from ..__common__ import add


reverse = lambda i, e="strict": (i[::-1], len(i))
add("reverse", reverse, reverse)

word_reverse = lambda i, e="strict": (" ".join(w[::-1] for w in i.split()), len(i))
add("reverse-words", word_reverse, word_reverse, r"^reverse[-_]words$")

