# -*- coding: UTF-8 -*-
"""UU Codec - UU content encoding, relying on the native uu package.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from io import BytesIO
from uu import decode as _dec, encode as _enc

from ..__common__ import *


__examples__ = {
    'enc(uu|uu_codec)': {'this is a test': "begin 666 -\n.=&AI<R!I<R!A('1E<W0 \n \nend\n"},
    'dec(uu-encode)':   {'.=&AI<R!I<R!A(\'1E<W0 ': "this is a test"},
    'dec(uuencode)':    {'.=&AI<R!I<R!A(\'1E<W0`': "this is a test"},
    'dec(uu-codec)':    {'begin 666 -\n.=&AI<R!I<R!A(\'1E<W0`': "this is a test"},
    'dec(uu_codec)':    {'\n.=&AI<R!I<R!A(\'1E<W0`\n\n\n`\nend': "this is a test"},
}


def uu_encode(text, errors="strict"):
    out = BytesIO()
    _enc(BytesIO(b(text)), out)
    return out.getvalue(), len(text)


def uu_decode(text, errors="strict"):
    t = b(text).strip(b"\n")
    if not re.match(b"^begin [1-7]{3} .*$", t.split(b"\n")[0]):
        t = b"begin 666 -\n" + t
    if not re.match(b"^end$", t.split(b"\n")[-1]):
        t += [b"", b"`"][t[-1] == b"`"] + b"\nend"
    out = BytesIO()
    _dec(BytesIO(t), out, quiet=True)
    out = out.getvalue()
    while out.endswith(b"\x00" * 42):
        out = out[:-42]
    return out, len(text)


add("uu", uu_encode, uu_decode, pattern=r"^uu(?:[-_]?encode|[-_]codec)?$",
    bonus_func=lambda o, *a: re.match(b"^begin [1-7]{3} .*\n.*\nend$", b(o.text).strip(b"\n"), re.M))

