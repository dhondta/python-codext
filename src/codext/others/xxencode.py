# -*- coding: UTF-8 -*-
"""XX Codec - xxencode content encoding.

xxencode works like uuencode, but with an alphabet made of "+", "-", digits and letters only, so that the encoded data
 survives character set conversions (e.g. to EBCDIC). Each line encodes up to 45 bytes in groups of 3 bytes written as
 4 characters, and starts with the character holding its number of bytes. The lines are framed by a "begin" line and an
 "end" line, preceded by an empty data line ("+").

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Xxencoding
"""
from string import ascii_lowercase as LC, ascii_uppercase as UC, digits as DG

from ..__common__ import *


__examples__ = {
    'enc(xx|xxencode|xx-encode|xx_codec)': {'Cat': "begin 666 -\n1Eq3o\n+\nend\n"},
    'dec(xx)':          {'1Eq3o': "Cat", 'begin 644 cat.txt\r\n1Eq3o\r\n+\r\nend\r\n': "Cat", '1Eq!o': None,
                         '3Eq3o': None, '!Eq3o': None,
                         'begin 644 cat.txt\n\n1Eq3o++++\n+\nend': "Cat"},
    'dec(xxencode)':    {'begin 644 wikipedia-url.txt\nOO5FoQ1cj9rRrRmtrOKhdQ4JYOK2iPr7b1Ec+\n+\nend':
                         "http://www.wikipedia.org\r\n"},
    'enc-dec(xx)':      ["", "this is a test", "@random{512,1024,2048}"],
}


XX = "+-" + DG + UC + LC


def xx_encode(text, errors="strict"):
    data, r = b(text), ["begin 666 -"]
    for i in range(0, len(data), 45):
        chunk, line = data[i:i+45], XX[len(data[i:i+45])]
        for j in range(0, len(chunk), 3):
            n = int.from_bytes(chunk[j:j+3].ljust(3, b"\0"), "big")
            line += "".join(XX[n >> s & 63] for s in (18, 12, 6, 0))
        r.append(line)
    return (s := "\n".join(r + ["+", "end", ""])), len(s)


def xx_decode(text, errors="strict"):
    _h = handle_error("xx", errors, decode=True, kind="token", item="line")
    lines, r = [l.strip() for l in ensure_str(text).strip().splitlines()], b""
    if len(lines) > 0 and re.match(r"^begin [0-7]{3,4} ", lines[0]):
        lines = lines[1:]
    if len(lines) > 0 and lines[-1] == "end":
        lines = lines[:-1]
    for k, l in enumerate(lines):
        if l == "":
            continue
        # the first character holds the number of bytes of the line ; "+" (0) marks the end of the data
        if (n := XX.find(l[0])) == 0:
            break
        out, data, size = b"", l[1:], 0
        if n < 0:
            r += b(_h(l[0], k))
            n = len(data) * 3 // 4
        # each group of 4 characters holds 3 bytes, the last one being truncated to the announced number of bytes ; an
        #  invalid group is handled as a whole, extra groups (padding) being discarded
        for j in range(0, len(data), 4):
            if size >= n:
                break
            g, t = data[j:j+4], min(3, n - size)
            size += t
            if any(c not in XX for c in g):
                out += b(_h(g, k))
                continue
            v = 0
            for c in g.ljust(4, "+"):
                v = v << 6 | XX.index(c)
            out += v.to_bytes(3, "big")[:t]
        r += out if size == n else out + b(_h(l, k))
    return r, len(r)


add("xx", xx_encode, xx_decode, r"^xx(?:[-_]?encode|[-_]codec)?$",
    bonus_func=lambda o, *a: re.match(r"^begin [0-7]{3,4} .*\n(?:.*\n)*\+\nend$", ensure_str(o.text).strip(), re.M))
