# -*- coding: UTF-8 -*-
"""COBS Codec - Consistent Overhead Byte Stuffing content encoding.

Consistent Overhead Byte Stuffing (COBS), by Stuart Cheshire and Mary Baker (1999), removes the zero bytes of the data,
 so that a zero byte can be used to delimit packets: the data is split at its zero bytes, each block being preceded by a
 code byte giving its length plus one (hence the distance to the next zero byte), a block of 254 non-zero bytes being
 written with the code 255 and followed by no zero byte. The overhead is of 1 byte per 254 bytes at most.

Encoding does not add the zero byte delimiting the packet, as CyberChef, and decoding rejects any zero byte, while the
 "-delimited" variant adds it after the encoded data and requires it when decoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Consistent_Overhead_Byte_Stuffing
"""
from ..__common__ import *


__examples__ = {
    # examples of Wikipedia (without the delimiter)
    'enc(cobs|consistent-overhead-byte-stuffing)': {
        '\x00': "\x01\x01", '\x00\x00': "\x01\x01\x01", '\x00\x11\x00': "\x01\x02\x11\x01",
        '\x11\x22\x00\x33': "\x03\x11\x22\x02\x33", '\x11\x22\x33\x44': "\x05\x11\x22\x33\x44",
        '\x11\x00\x00\x00': "\x02\x11\x01\x01\x01", '': "",
        "".join(map(chr, range(1, 255))): "\xff" + "".join(map(chr, range(1, 255))),
        "".join(map(chr, range(0, 255))): "\x01\xff" + "".join(map(chr, range(1, 255))),
        "".join(map(chr, range(1, 256))): "\xff" + "".join(map(chr, range(1, 255))) + "\x02\xff",
        "".join(map(chr, range(2, 256))) + "\x00": "\xff" + "".join(map(chr, range(2, 256))) + "\x01\x01",
        "".join(map(chr, range(3, 256))) + "\x00\x01": "\xfe" + "".join(map(chr, range(3, 256))) + "\x02\x01",
    },
    'enc(cobs-delimited|cobs_delimited)': {'\x11\x22\x00\x33': "\x03\x11\x22\x02\x33\x00"},
    'dec(cobs)': {'\x03\x11\x22\x02\x33': "\x11\x22\x00\x33", '\x00HELLO': None, 'HE\x00LLO': None, 'HELLO\x00': None,
                  '\x05\x11\x22': None},
    'dec(cobs-delimited)': {'\x03\x11\x22\x02\x33\x00': "\x11\x22\x00\x33", '\x03\x11\x22\x02\x33': None,
                            '\x03\x11\x00\x02\x33\x00': None},
    'enc-dec(cobs|cobs-delimited)': ["test", "This is a test", "\x00\x00\x00", "@random{512,1024,2048}"],
}
__guess__ = ["cobs", "cobs-delimited"]


def cobs_encode(delimited=""):
    def encode(text, errors="strict"):
        t, r, block = b(text), bytearray(), bytearray()
        # each block of non-zero bytes ending at a zero byte is preceded by its length plus one, while a block of 254
        #  bytes is preceded by 255 and is not followed by a zero byte
        for byte in t:
            if byte == 0:
                r += bytes([len(block) + 1]) + block
                block = bytearray()
                continue
            block.append(byte)
            if len(block) == 254:
                r += b"\xff" + block
                block = bytearray()
        # the data is seen as followed by a zero byte (not written), ending a last block unless the data ends with a
        #  block of 254 bytes
        if block or t[-1:] == b"\x00":
            r += bytes([len(block) + 1]) + block
        return bytes(r) + (b"\x00" if delimited else b""), len(t)
    return encode


def cobs_decode(delimited=""):
    def decode(text, errors="strict"):
        t, _h, r = b(text), handle_error("cobs", errors, decode=True, kind="byte"), bytearray()
        if delimited:
            # the packet must be delimited by a zero byte, which is removed
            if t[-1:] != b"\x00":
                _h(t[-1:], len(t) - 1)
            else:
                t = t[:-1]
        if b"\x00" in t:
            # no zero byte is allowed in the encoded data
            i = t.index(b"\x00")
            _h(t[i:i+1], i)
            t = t.replace(b"\x00", b"")
        i = 0
        while i < len(t):
            code = t[i]
            block = t[i+1:i+code]
            if len(block) < code - 1:
                # the block is cut by the end of the data
                _h(t[i:i+1], i, bytes(r))
            r += block
            i += code
            if code < 255 and i < len(t):
                r.append(0)
        return bytes(r), len(text)
    return decode


add("cobs", cobs_encode, cobs_decode, r"^(?:cobs|consistent[-_]overhead[-_]byte[-_]stuffing)([-_]delimited)?$",
    expansion_factor=(1., .1))
