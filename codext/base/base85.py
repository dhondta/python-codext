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


__examples__ = {'enc(base85|base-85|base_85)': {'this is a test': "bZBXFAZc?TVIXv6b94"}}


#FIXME: implement Z85 (ZeroMQ) in base85.py ; cfr spec https://rfc.zeromq.org/spec/32/
#FIXME: implement base85-rfc1924 in base85.py
#B85 = {
#    r'':               "!\"#$%&'()*+,-./" + digits + ":;<=>?@" + upper + "[\\]^_`" + lower[:21],
#    r'[-_]z(eromq)?$': digits + upper + lower + ".-:+=^!/*?&<>()[]{}@%$#",
#    r'[-_]rfc1924$':   digits + upper + lower + "!#$%&()*+-;<=>?@^_`{|}~",
#}
#base(B85, r"^base[-_]?85(|[-_](?:z(?:eromq)?|rfc1924))$")


if PY3:
    def base85_encode(input, errors='strict'):
        return base64.b85encode(b(input)), len(input)

    def base85_decode(input, errors='strict'):
        return base64.b85decode(b(input)), len(input)

    add("base85", base85_encode, base85_decode, r"^base[-_]?85$", entropy=7.05)

