# -*- coding: UTF-8 -*-
"""PNG IDAT Codec - data compressed into the IDAT chunks of a PNG image.

In a PNG image, the pixels are compressed with zlib (the DEFLATE algorithm, i.e. LZ77 and Huffman coding) and stored in
 one or more IDAT chunks, each one made of:
- the length of its data (4 bytes, big-endian)
- its type ("IDAT", 4 bytes)
- its data, a part of the zlib stream, which is made of a header (compression method and flags, 2 bytes), the compressed
   blocks and the Adler-32 checksum of the uncompressed data (4 bytes)
- the CRC-32 of its type and data (4 bytes)

Encoding compresses the input into a zlib stream and wraps it into a single IDAT chunk, or into chunks holding at most N
 bytes each with "png-idat-N" (as PNG encoders usually split the stream, e.g. into chunks of 8192 bytes). Decoding
 concatenates the data of the IDAT chunks of the input, which can also be a whole PNG image (its other chunks being
 ignored), and decompresses it ; for a PNG image, this gives its raw pixel data (the scanlines, each preceded by its
 filter type byte). A chunk whose CRC-32 does not match is an error, unless errors are not handled strictly.

NB: Not an encoding properly speaking.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://www.w3.org/TR/png-3/#5Chunk-layout
"""
import zlib
from struct import pack, unpack

from ..__common__ import *


__examples__ = {
    'enc(png-idat|png_idat|pngidat|idat)': {'test': "\x00\x00\x00\x0cIDATx\xda+I-.\x01\x00\x04]\x01\xc1hU\xe3q"},
    'dec(png-idat)': {'\x00\x00\x00\x0cIDATx\xda+I-.\x01\x00\x04]\x01\xc1hU\xe3q': "test",
                      '\x00\x00\x00\x0cIDATx\xda+I-.\x01\x00\x04]\x01\xc1hU\xe3p': None,
                      '\x00\x00\x00\x0cIDATx\xda+I-.\x01\x00\x04]\x01\xc1hU\xe3': None,
                      '\x00\x00\x00\x00IEND\xaeB`\x82': None, 'test': None,
                      '\x00\x00\x00\x08IDATnot zlibUi\x11\xf7': None,
                      # a whole PNG image (1x1 pixel, 8-bit grayscale): its filter type byte and its pixel
                      '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x00\x00\x00\x00:~\x9bU'
                      '\x00\x00\x00\nIDATx\xdac\xa8\x07\x00\x00\x81\x00\x80~\x1c)\xc7'
                      '\x00\x00\x00\x00IEND\xaeB`\x82': "\x00\x7f"},
    'enc-dec(png-idat|png-idat-1|png-idat-8|png-idat-8192)': ["test", "This is a test", "@random{512,1024,2048}"],
}
__guess__ = ["png-idat"]


SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _chunk(data, ctype=b"IDAT"):
    return pack(">I", len(data)) + ctype + data + pack(">I", zlib.crc32(ctype + data))


def pngidat_encode(size=None):
    size = int(size) if size else None
    def encode(text, errors="strict"):
        if len(text) == 0:
            return "", 0
        z = zlib.compress(b(text), 9)
        n = size or len(z)
        return b"".join(_chunk(z[i:i+n]) for i in range(0, len(z), n)), len(text)
    return encode


def pngidat_decode(size=None):
    def decode(data, errors="strict"):
        if len(data) == 0:
            return "", 0
        data, _h = b(data), handle_error("png-idat", errors, decode=True, kind="chunk")
        # a whole PNG image starts with its signature, followed by its chunks
        i, idat = len(SIGNATURE) if data.startswith(SIGNATURE) else 0, []
        while i < len(data):
            if len(data) - i < 12 or len(data) - i < 12 + (n := unpack(">I", data[i:i+4])[0]):
                return _h(data[i+4:i+8], i), len(data)  # truncated chunk
            ctype, chunk = data[i+4:i+8], data[i+8:i+8+n]
            if ctype == b"IDAT":
                # a chunk whose CRC-32 does not match is still used if errors are not handled strictly
                if unpack(">I", data[i+8+n:i+12+n])[0] != zlib.crc32(ctype + chunk) and errors == "strict":
                    return _h(ctype, i), len(data)
                idat.append(chunk)
            i += 12 + n
        if len(idat) == 0:
            return _h(data[:8], 0), len(data)
        try:
            r = zlib.decompress(b"".join(idat))
        except zlib.error:
            return _h(data[:8], 0), len(data)
        return r, len(data)
    return decode


add("png-idat", pngidat_encode, pngidat_decode, plain="bytes", encoded="bytes",
    pattern=r"^(?:png[-_]?)?idat(?:[-_]([1-9][0-9]*))?$", expansion_factor=None,
    bonus_func=lambda o, *a: o.text[4:8] == "IDAT" or b(o.text).startswith(SIGNATURE))
