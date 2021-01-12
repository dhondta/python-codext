# -*- coding: UTF-8 -*-
"""Gzip Codec - gzip content compression.

NB: Not an encoding properly speaking.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
import zlib
from gzip import GzipFile

from ..__common__ import *


__examples__ = {'enc-dec(gzip)': ["test", "This is a test"]}
__guess__ = ["gzip"]


def gzip_encode(text, errors="strict"):
    out = BytesIO()
    with GzipFile(fileobj=out, mode="wb") as f:
        f.write(b(text))
    return out.getvalue(), len(text)


def gzip_decode(data, errors="strict"):
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


add("gzip", gzip_encode, gzip_decode, entropy=7.9)

