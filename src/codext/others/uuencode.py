# -*- coding: UTF-8 -*-
"""UU Codec - UU content encoding, relying on the native uu package.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from binascii import a2b_uu as _dec, b2a_uu as _enc

from ..__common__ import *


__examples__ = {
    'enc(uu|uu_codec)': {'this is a test': "begin 666 -\n.=&AI<R!I<R!A('1E<W0 \n \nend\n"},
    'dec(uu-encode)':   {'.=&AI<R!I<R!A(\'1E<W0 ': "this is a test", '.=&AI<R!I<R!A(\'1E<W0`': "this is a test"},
    'dec(uu-codec)':    {'begin 666 -\n.=&AI<R!I<R!A(\'1E<W0`': None, '.=&AI<R!I<R!A(\'1E<W0`\n\n\n`\nend': None},
    'dec(uu_codec)':    {'begin 777 test.txt\n.=&AI<R!I<R!A(\'1E<W0`\n\n\n`\nend': "this is a test"},
    'enc-dec(uu)':      ["begin 666 -\n.=&AI<R!I<R!A(\'1E<W0`", "@random{512,1024,2048}"],
}


def uu_encode(text, errors="strict"):
    r, t = b"begin 666 -\n", b(text)
    for i in range(0, len(t), 45):
        r += _enc(t[i:i+45])
    return r + b" \nend\n", len(text)


def uu_decode(text, errors="strict"):
    h = handle_error("uu", "strict", decode=True, kind="token", item="line")
    lines = b(text).strip(b" \t\r\n\f").split(b"\n")
    start, end = re.match(b"^begin [1-7]{3} .*$", lines[0]), re.match(b"^end$", lines[-1])
    if start and end:
        lines = lines[1:-1]
    elif not start and not end:
        pass
    else:
        if errors == "ignore":
            lines = lines[1:] if start else lines[:-1]
        elif end:
            h(lines[0], 0)
        elif start:
            h(lines[-1], len(lines)-1)
    while len(lines) > 0 and lines[-1].strip(b" \t\r\n\f") in [b"", b"`"]:
        lines = lines[:-1]
    r = b""
    for l in lines:
        r += _dec(l.strip(b" \t\r\n\f"))
    return r, len(text)


add("uu", uu_encode, uu_decode, pattern=r"^uu(?:[-_]?encode|[-_]codec)?$",
    bonus_func=lambda o, *a: re.match(b"^begin [1-7]{3} .*\n.*\nend$", b(o.text).strip(b"\n"), re.M))

