# -*- coding: UTF-8 -*-
"""LZ78 Codec - Lempel-Ziv 1978 compression algorithm.

NB: Not an encoding properly speaking.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Inspired from: https://github.com/mileswatson/lempel-ziv-compression
"""
from ..__common__ import *


__examples__ = {'enc-dec(lz78)': ["test", "This is a test", "@random{512,1024,2048}"]}


def lz78_compress(input, errors="strict"):
    """ Compresses the given data by applying LZ78 compression algorithm. """
    data = tuple(c if isinstance(c, int) else ord(c) for c in input)
    if len(data) == 0:
        return "", 0
    out = (data[0], )
    d = {tuple(): (0, ), (data[0], ): (1, )}
    a, b, ctr = 1, 1, [2]
    while b < len(data):
        if not data[a:b+1] in d:
            w = d[data[a:b]]
            out += w + tuple(0 for i in range(len(ctr) - len(w) - int(sum(ctr) == 1))) + (data[b], )
            d[data[a:b+1]] = tuple(ctr)
            for i in range(len(ctr)):
                ctr[i] += 1
                if ctr[i] != 256:
                    break
                else:
                    ctr[i] = 0
                    if i == len(ctr) - 1:
                        ctr.append(1)
            a = b + 1
        b += 1
    if data[a:b] in d and a != b:
        w = tuple(d[data[a:b]])
        out += w + tuple(0 for i in range(len(ctr) - len(w)))
    return "".join(chr(i) for i in out), len(out)


def lz78_decompress(input, errors="strict"):
    """ Decompresses the given data. """
    data = tuple(c if isinstance(c, int) else ord(c) for c in input)
    if len(data) == 0:
        return "", 0
    out = (data[0], )
    l = [tuple(), out]
    a, b, c, i, char = 1, 1, 256, 0, False
    try:
        while a < len(data):
            if char:
                out += (data[a], )
                l.append(l[i] + (data[a], ))
                char = False
                a += 1
                if len(l) == c + 1:
                    b += 1
                    c *= 256
            else:
                i, m = 0, 1
                for j in range(b):
                    i += data[a + j] * m
                    m *= 256
                out += l[i]
                a += b
                char = True
    except:
        return handle_error("lz78", errors, decode=True)(chr(data[a]), a), len(input)
    return "".join(chr(i) for i in out), len(out)


add("lz78", lz78_compress, lz78_decompress)

