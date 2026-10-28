# -*- coding: UTF-8 -*-
"""BinHex Codec - BinHex 4.0 content encoding.

BinHex 4.0 (.hqx) is the binary-to-text encoding of the classic Mac OS. The data is stored as the data fork of a file
 made of:
- a header: the name length (1 byte), the name, a version byte (0), the type and creator codes (4 bytes each), the
   Finder flags (2 bytes), the lengths of the data and resource forks (4 bytes each) and a CRC (2 bytes)
- the data fork, followed by its CRC
- the resource fork (empty here), followed by its CRC

The CRC is CRC-16/XMODEM. This stream is compressed with run-length encoding (a run of 4 to 255 bytes is written as the
 byte, the marker 0x90 and the run length ; a literal 0x90 is written as 0x90 0x00), then encoded with 6 bits per
 character, framed by ":" and wrapped in lines of 64 characters after the "(This file must be converted with BinHex
 4.0)" line.

When decoding, the text before the data (e.g. the introduction line) and whitespaces are ignored, the CRCs are checked
 and the data fork is returned.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://datatracker.ietf.org/doc/html/rfc1741
"""
from binascii import crc_hqx

from ..__common__ import *


__examples__ = {
    'enc(binhex|binhex4|binhex-4.0|hqx)': {'Hello': "(This file must be converted with BinHex 4.0)\n\n"
                                                    ":!5d!2j!)!*!&\"3#3\"$X55'9XE'r,eJ!!:\n"},
    'dec(binhex)':      {'This is a test': None, ":!5d!2j!)!*!&\"3#3\"$X55'9XE'r,eJ!!": None,
                         ":!5e!2j!)!*!&\"3#3\"$X55'9XE'r,eJ!!:": None, ":!5d!2j!)!*!&\"3#3\"$X55'9XF'r,eJ!!:": None,
                         ":!5d!2j!)!*!&\"3#3\"$X55'9XE'r,eK!!:": None, ":!5d!2j!)!*!&\"3#3\"$X55:": None,
                         ":!5d!2j!)!*!&\"3#3\"$X55'9~E'r,eJ!!:": None, "::": None, ":N!8:": None},
    'dec(hqx)':         {"junk\r\n:!5d!2j!)!*!&\"3#3\"$X55'9X\r\nE'r,eJ!!:\r\njunk": "Hello"},
    'enc-dec(binhex)':  ["", "Hello, World!", "\x90\x90AAAAAAAAB\x90", "A" * 300, "@random{512,1024,2048}"],
}


HQX = "!\"#$%&'()*+,-012345689@ABCDEFGHIJKLMNPQRSTUVXYZ[`abcdefhijklmpqr"
INTRO, RUNCHAR = "(This file must be converted with BinHex 4.0)", 0x90


def binhex_encode(text, errors="strict"):
    data, name = b(text), b"-"
    # header (unknown type and creator codes, no Finder flags, empty resource fork), then forks with their CRCs
    s = bytes([len(name)]) + name + b"\0" + b"????" * 2 + b"\0\0" + len(data).to_bytes(4, "big") + b"\0" * 4
    s += crc_hqx(s, 0).to_bytes(2, "big") + data + crc_hqx(data, 0).to_bytes(2, "big") + b"\0\0"
    # run-length encoding
    rle, i = bytearray(), 0
    while i < len(s):
        if (c := s[i]) == RUNCHAR:
            rle += bytes([RUNCHAR, 0])
            i += 1
            continue
        n = 1
        while i + n < len(s) and s[i+n] == c and n < 255:
            n += 1
        rle += bytes([c, RUNCHAR, n]) if n > 3 else bytes([c]) * n
        i += n
    # 6-bit encoding, the last character being padded with zero bits
    bits = "".join(f"{x:08b}" for x in rle)
    bits += "0" * (-len(bits) % 6)
    r = ":" + "".join(HQX[int(bits[i:i+6], 2)] for i in range(0, len(bits), 6)) + ":"
    r = "\n".join(r[i:i+64] for i in range(0, len(r), 64))
    return (r := f"{INTRO}\n\n{r}\n"), len(r)


def binhex_decode(text, errors="strict"):
    _h = handle_error("binhex", errors, decode=True)
    _f = handle_error("binhex", "strict", decode=True, kind="field", item="section")
    text = ensure_str(text)
    # the data starts after the first colon (that follows the introduction line, if any) and ends with the next one
    start = text.find(":", text.find(INTRO) + 1 if INTRO in text else 0)
    end = text.find(":", start + 1)
    if start < 0 or end < 0:
        if errors == "strict":
            handle_error("binhex", errors, decode=True, kind="missing delimiter")(":", len(text))
        # in non-strict modes, without delimiter, there is no data or it runs until the end of the text
        if start < 0:
            return b"", 0
        end = len(text)
    bits = []
    for i, c in enumerate(text[start+1:end], start + 1):
        if c in HQX:
            bits.append(f"{HQX.index(c):06b}")
        elif not c.isspace():
            # a wrong character cannot be replaced in the binary stream, hence it is dropped
            _h(c, i)
    bits = "".join(bits)
    rle = [int(bits[i:i+8], 2) for i in range(0, len(bits) - 7, 8)]
    # run-length decoding
    s, i = bytearray(), 0
    while i < len(rle):
        if (c := rle[i]) == RUNCHAR and i + 1 < len(rle):
            if (n := rle[i+1]) == 0:
                s.append(RUNCHAR)
            elif len(s) > 0:
                s += bytes([s[-1]]) * (n - 1)
            elif errors == "strict":
                # a run cannot start the stream, as it repeats the previous byte
                _f(f"0x90 0x{n:02x}", "data")
            i += 2
            continue
        s.append(c)
        i += 1
    # header parsing and CRCs checks ; in non-strict modes, what is available from the data fork is returned
    n = s[0] if len(s) > 0 else 0
    hlen, dlen, rlen = n + 20, int.from_bytes(s[n+12:n+16], "big"), int.from_bytes(s[n+16:n+20], "big")
    for name, pos, length in [("header", 0, hlen), ("data fork", hlen + 2, dlen), ("resource fork", hlen + dlen + 4,
                                                                                    rlen)]:
        if len(s) < pos + length + 2:
            if errors == "strict":
                _f("length", name)
            break
        if errors == "strict" and int.from_bytes(s[pos+length:pos+length+2], "big") != crc_hqx(s[pos:pos+length], 0):
            _f("CRC", name)
    return (r := bytes(s[hlen+2:hlen+2+dlen])), len(r)

add("binhex", binhex_encode, binhex_decode, r"^(?:binhex(?:[-_]?4(?:\.0)?)?|hqx)$",
    bonus_func=lambda o, *a: INTRO in ensure_str(o.text))
