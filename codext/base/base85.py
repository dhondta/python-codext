# -*- coding: UTF-8 -*-
"""Base85 Codec - base85 content encoding.

This is a simple wrapper for adding base64.b85**code to the codecs.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
import base64

from ..__common__ import *


if PY3:
    def base85_encode(input, errors='strict'):
        return base64.b85encode(b(input)), len(input)

    def base85_decode(input, errors='strict'):
        return base64.b85decode(b(input)), len(input)

    add("base85", base85_encode, base85_decode, r"^base[-_]?85$")

