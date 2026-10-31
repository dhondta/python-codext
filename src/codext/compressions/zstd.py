# -*- coding: UTF-8 -*-
"""Zstandard Codec - zstd content compression.

Zstandard (zstd), created by Yann Collet at Facebook in 2015 and specified in RFC 8878, combines LZ77-style matching
 with entropy coding (Huffman coding for the literals and finite-state entropy for the sequences), in frames with a
 magic number (0xFD2FB528). This codec relies on the compression.zstd module of the standard library (Python 3.14 and
 later) or on its backport (the backports.zstd package, installed as a dependency for the previous versions of Python),
 and is not available without them. The compression level is given with the codec name (from 1 to 22, e.g. "zstd-19")
 and defaults to 3 ; decoding handles concatenated frames.

NB: Not an encoding properly speaking.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://datatracker.ietf.org/doc/html/rfc8878
"""
from ..__common__ import *

try:
    from compression import zstd
except ImportError:
    try:
        from backports import zstd
    except ImportError:
        zstd = None


__examples__ = {
    'dec(zstd)': {'(\xb5/\xfd \x04!\x00\x00test': "test", '(\xb5/\xfd \x04!\x00\x00tes': None, 'test': None},
    'enc-dec(zstd|zstandard|zstd-1|zstd_19|zstd-22)': ["", "test", "This is a test", "@random{512,1024,2048}"],
}


def zstd_compress(level=None):
    def compress(text, errors="strict"):
        lvl = level or 3
        if lvl not in range(1, 23):
            raise LookupError("Bad parameter for encoding 'zstd': compression level must be between 1 and 22")
        # the compressed data is given as latin-1 text (or bytes), so that it is read back as is
        return zstd.compress(b(ensure_str(text)), level=lvl).decode("latin-1"), len(text)
    return compress


def zstd_decompress(level=None):
    def decompress(text, errors="strict"):
        data = b(ensure_str(text))
        try:
            r = zstd.decompress(data)
        except zstd.ZstdError:
            return handle_error("zstd", errors, decode=True)(data[:1].decode("latin-1"), 0), len(text)
        return r, len(text)
    return decompress


if zstd is not None:
    add("zstd", zstd_compress, zstd_decompress, r"^(?:zstd|zstandard)(?:[-_](\d{1,2}))?$", examples=__examples__)
