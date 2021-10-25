# -*- coding: UTF-8 -*-
"""Pkzip Codec - pkzip content compression.

NB: Not an encoding properly speaking.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
import zipfile

from ..__common__ import *


_str          = ["test", "This is a test", "@random{512,1024,2048}"]
__examples1__ = {'enc-dec(pkzip-deflate|deflate)': _str}
__examples2__ = {'enc-dec(pkzip_bz2|bzip2)':       _str}
__examples3__ = {'enc-dec(pkzip-lzma|lzma)':       _str}


if PY3:
    def pkzip_encode(compression_type):
        def _encode(text, errors="strict"):
            c = zipfile._get_compressor(compression_type)
            return c.compress(b(text)) + c.flush(), len(text)
        return _encode


    def pkzip_decode(compression_type, name):
        def _decode(data, errors="strict"):
            d = zipfile._get_decompressor(compression_type)
            r = d.decompress(b(data))
            if len(r) == 0:
                return handle_error(name, errors, decode=True)(data[0], 0) if len(data) > 0 else "", len(data)
            return r, len(r)
        return _decode


    add("pkzip_deflate", pkzip_encode(8), pkzip_decode(8, "deflate"), r"(?:(?:pk)?zip[-_])?deflate",
        entropy=7.9, examples=__examples1__, guess=["deflate"])

    add("pkzip_bzip2", pkzip_encode(12), pkzip_decode(12, "bzip2"), r"(?:(?:pk)?zip[-_])?bz(?:ip)?2",
        entropy=7.9, examples=__examples2__, guess=["bz2"])

    add("pkzip_lzma", pkzip_encode(14), pkzip_decode(14, "lzma"), r"(?:(?:pk)?zip[-_])?lzma",
        entropy=7.9, examples=__examples3__, guess=["lzma"])

