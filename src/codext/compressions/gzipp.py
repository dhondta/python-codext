# -*- coding: UTF-8 -*-
"""Gzip Codec - gzip content compression.

Gzip is the file format and compression tool created by Jean-loup Gailly and Mark Adler in 1992 for the GNU project,
 using the DEFLATE algorithm (LZ77 and Huffman coding) with a header and a CRC-32 trailer. This codec relies on Python's
 gzip module ; decoding is tried with and without the gzip file signature.

NB: Not an encoding properly speaking.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://datatracker.ietf.org/doc/html/rfc1952
"""
import zlib
from gzip import GzipFile

from ..__common__ import *


__examples__ = {'enc-dec(gzip)': ["test", "This is a test", "@random{512,1024,2048}"]}


def gzip_compress(text, errors="strict"):
    out = BytesIO()
    with GzipFile(fileobj=out, mode="wb") as f:
        f.write(b(text))
    return out.getvalue(), len(text)


def gzip_decompress(data, errors="strict"):
    # then try decompressing considering the file signature
    try:
        with GzipFile(fileobj=BytesIO(b(data)), mode="rb") as f:
            r = f.read()
    except:
        pass
    # try decompressing without considering the file signature
    try:
        r = zlib.decompress(b(data), 16 + zlib.MAX_WBITS)
    except:
        return handle_error("gzip", errors, decode=True)(data[0], 0) if len(data) > 0 else "", len(data)
    return r, len(r)


add("gzip", gzip_compress, gzip_decompress)

