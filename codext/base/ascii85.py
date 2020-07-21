# -*- coding: UTF-8 -*-
"""ASCII85 Codec - ascii85 content encoding.

This is a simple wrapper for adding base64.a85**code to the codecs.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
import base64

from ..__common__ import *


__examples__ = {'enc(ascii85|ascii-85|ascii_85)': {'this is a test': "FD,B0+DGm>@3BZ'F*%"}}


if PY3:
    def ascii85_encode(input, errors='strict'):
        return base64.a85encode(b(input)), len(input)

    def ascii85_decode(input, errors='strict'):
        return base64.a85decode(b(input)), len(input)

    add("ascii85", ascii85_encode, ascii85_decode, r"^ascii[-_]?85$")

