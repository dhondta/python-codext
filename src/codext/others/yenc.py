# -*- coding: UTF-8 -*-
"""yEnc Codec - yEnc content encoding.

yEnc is a binary-to-text encoding designed for Usenet. Each byte is shifted by 42 (modulo 256) and only the critical
 characters are escaped with "=" followed by the character shifted by 64 more: NUL, LF, CR and "=", as well as TAB and
 SPACE at the beginning or the end of a line and "." at the beginning of a line.

Three forms are supported:
- raw (default): the encoded data on a single line
- wrapped: the encoded data in lines of the given length (a line ending with an escape may be one character longer)
- full: the wrapped data framed by the "=ybegin" header and the "=yend" trailer holding its size and CRC32

When decoding, the header and the trailer are detected (the size and the CRC32 being checked) and line breaks are
 ignored, so that every form is decoded.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: http://www.yenc.org/yenc-draft.1.3.txt
"""
from zlib import crc32

from ..__common__ import *


__examples__ = {
    'enc(yenc|y-enc|y_enc)': {'Hello': "r\x8f\x96\x96\x99", '\xd6\xe0\xe3\x13': "=@=J=M=}"},
    'enc(yenc)':           {'\xf6\x04\xf6': "=`.=`", '\x04\xf6\x04': "=n .", '\xdf\xdf': "=I=I"},
    'enc(yenc-4)':         {'\xf6\xf6\xf6\xf6\xf6': "=` =`\r\n=`=`"},
    'enc(yenc-full)':      {'Hello': "=ybegin line=128 size=5 name=-\r\nr\x8f\x96\x96\x99\r\n"
                                     "=yend size=5 crc32=f7d18982\r\n"},
    'dec(yenc)':           {'r\x8f\r\n\x96\x96\x99': "Hello", 'r=': None, 'Ā': None},
    'dec(yenc-full)':      {'junk\n=ybegin part=1 line=128 size=5 name=hello.txt\n=ypart begin=1 end=5\nr\x8f\x96\x96'
                            '\x99\n=yend size=5 part=1 pcrc32=f7d18982\njunk': "Hello",
                            '=ybegin line=128 size=5 name=-\nr\x8f\x96\x96\x99\n=yend size=5 crc32=00000000': None,
                            '=ybegin line=128 size=5 name=-\nr\x8f\x96\x96\x99\n=yend size=4': None,
                            '=ybegin line=128 size=5 name=-\nr\x8f\x96\x96\x99': None},
    'enc-dec(yenc|yenc-1|yenc-2|yenc-128|yenc-full|yenc-3-full)': ["", "Hello, World!", "\x00\n\r=\t .",
                                                                   "@random{512,1024,2048}"],
}


CRITICAL, WHITESPACES = (0, 10, 13, 61), (9, 32)


def yenc_encode(line=None, full=None):
    line = line or (128 if full else 0)
    def encode(text, errors="strict"):
        data, lines, cur = b(text), [], ""
        for i, x in enumerate(data):
            o = (x + 42) % 256
            last = i == len(data) - 1 or line and len(cur) + 1 >= line
            if o in CRITICAL or not cur and o in WHITESPACES + (46, ) or last and o in WHITESPACES:
                cur += "=" + chr((o + 64) % 256)
            else:
                cur += chr(o)
            # an escape sequence is never split, hence a line may be one character longer
            if line and len(cur) >= line:
                lines.append(cur)
                cur = ""
        if cur:
            lines.append(cur)
        r = "\r\n".join(lines)
        if full:
            r = f"=ybegin line={line} size={len(data)} name=-\r\n" + (r + "\r\n" if r else "") + \
                f"=yend size={len(data)} crc32={crc32(data):08x}\r\n"
        return r, len(r)
    return encode


def yenc_decode(line=None, full=None):
    def decode(text, errors="strict"):
        text, _h = ensure_str(text), handle_error("yenc", errors, decode=True)
        lines, start, end = text.split("\n"), None, None
        # the data is framed if a header line is found ; then, lines out of the frame are ignored
        for i, l in enumerate(lines):
            if start is None and l.startswith("=ybegin "):
                start = i
            elif start is not None and l.startswith("=yend"):
                end = i
                break
        if start is not None:
            header, trailer = __fields(lines[start]), __fields(lines[end]) if end is not None else {}
            data = lines[start+1:end]
            if len(data) > 0 and data[0].startswith("=ypart "):
                data = data[1:]
            text = "\n".join(data)
        r = []
        # tokens: an escaped character, a trailing escape character (error) or a plain character
        for m in re.finditer(r"=(.)|(=)\Z|(.)", text.replace("\r", "").replace("\n", ""), re.S):
            c = m.group(1) or m.group(2) or m.group(3)
            if m.group(2) or ord(c) > 255:
                r.extend(b(_h(c, m.start())))
            else:
                r.append((ord(c) - 64 * bool(m.group(1)) - 42) % 256)
        r = bytes(r)
        if start is not None and errors == "strict":
            _f = handle_error("yenc", errors, decode=True, kind="field", item="line")
            if end is None:
                _f("=yend", len(lines))
            size, crc = trailer.get("size", header.get("size")), trailer.get("pcrc32")
            if crc is None and "part" not in header:
                crc = trailer.get("crc32")
            if size is not None and size != str(len(r)):
                _f(f"size={size}", end)
            if crc is not None and crc.lower().zfill(8) != f"{crc32(r):08x}":
                _f(f"crc32={crc}", end)
        return r, len(r)
    return decode


def __fields(line):
    """ Parse the keyword=value fields of a header or trailer line (the name, possibly holding spaces, comes last). """
    return {k: v for k, v in re.findall(r"(\w+)=(\S*)", line.split(" name=")[0])}


add("yenc", yenc_encode, yenc_decode, r"^y[-_]?enc(?:[-_]([1-9][0-9]*))?([-_]full)?$",
    bonus_func=lambda o, *a: re.search(r"^=ybegin .*\n(?:.*\n)*=yend ", ensure_str(o.text), re.M))
