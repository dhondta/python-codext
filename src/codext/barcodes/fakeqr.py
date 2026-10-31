# -*- coding: UTF-8 -*-
"""Fake QR Codec - fake QR code content encoding.

This codec hides a text in something that looks like a QR code but is not a valid one: the input bytes are written as
 their bits, one module (a dark module for a 1, a light one for a 0) per bit, laid out row by row in the smallest
 QR-like square grid (versions 1 to 40, that is 21x21 up to 177x177 modules) that can hold them, skipping the three
 finder patterns (the squares in the corners) and the timing patterns (the dotted lines joining them) so that the
 result keeps the typical QR aspect. A 32-bit header holds the input length, hence the padding modules are ignored when
 decoding. An optional mask (one of the 8 QR mask patterns, given as a number in the codec name, e.g. "fakeqr-3")
 inverts part of the data modules depending on their coordinates, making the pixels look more random.

By default, the fake QR code is a grayscale PNG image (one pixel per module), but the "-text" variant (e.g.
 "fakeqr-text" or "fakeqr-text-3") renders it as plain text instead, with a full block for a dark module and a space
 for a light one, rows separated by newlines. Decoding accepts either form, auto-detecting the image from its PNG
 signature.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/QR_code
"""
import struct
import zlib

from ..__common__ import *


# QR-like square sizes, from version 1 (21x21) to version 40 (177x177)
_SIZES = [21 + 4 * v for v in range(40)]
# 7x7 finder pattern (1 = dark module), placed in three corners
_FINDER = [[1, 1, 1, 1, 1, 1, 1],
           [1, 0, 0, 0, 0, 0, 1],
           [1, 0, 1, 1, 1, 0, 1],
           [1, 0, 1, 1, 1, 0, 1],
           [1, 0, 1, 1, 1, 0, 1],
           [1, 0, 0, 0, 0, 0, 1],
           [1, 1, 1, 1, 1, 1, 1]]
# the 8 QR mask patterns, as functions of the (row, column) coordinates ; a true value inverts the data module
_MASKS = [lambda r, c: (r + c) % 2 == 0,
          lambda r, c: r % 2 == 0,
          lambda r, c: c % 3 == 0,
          lambda r, c: (r + c) % 3 == 0,
          lambda r, c: (r // 2 + c // 3) % 2 == 0,
          lambda r, c: (r * c) % 2 + (r * c) % 3 == 0,
          lambda r, c: ((r * c) % 2 + (r * c) % 3) % 2 == 0,
          lambda r, c: ((r + c) % 2 + (r * c) % 3) % 2 == 0]
_RESERVED = {}
_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_DARK, _LIGHT = "█", " "  # full block and space, for the plain text rendering


def _reserved(n):
    """ Set of the (row, column) coordinates of the modules reserved for the finder and timing patterns. """
    if n not in _RESERVED:
        res = set()
        for r0, c0 in ((0, 0), (0, n - 8), (n - 8, 0)):  # the finder patterns and their separators (8x8 blocks)
            for i in range(8):
                for j in range(8):
                    if 0 <= r0 + i < n and 0 <= c0 + j < n:
                        res.add((r0 + i, c0 + j))
        for i in range(n):  # the timing patterns (full row and column 6, the gap between the finder patterns)
            res.add((6, i))
            res.add((i, 6))
        _RESERVED[n] = res
    return _RESERVED[n]


def _grid_size(nbits):
    """ Smallest QR-like size whose data modules can hold the given number of bits. """
    for n in _SIZES:
        if n * n - len(_reserved(n)) >= nbits:
            return n
    raise ValueError("'fakeqr' codec can't encode input of more than %d bytes" % \
                     ((_SIZES[-1] ** 2 - len(_reserved(_SIZES[-1])) - 32) // 8))


def _decorate(grid, n):
    """ Draw the finder and timing patterns on the module grid. """
    for i in range(8, n - 8):  # timing patterns (alternating modules, starting dark next to the finders)
        grid[6][i] = grid[i][6] = int(i % 2 == 0)
    for r0, c0 in ((0, 0), (0, n - 7), (n - 7, 0)):  # finder patterns
        for i in range(7):
            for j in range(7):
                grid[r0 + i][c0 + j] = _FINDER[i][j]


def _png(n, raw):
    """ Wrap raw (filtered) scanlines as an 8-bit grayscale PNG image of size n. """
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d))
    return _SIGNATURE + chunk(b"IHDR", struct.pack(">IIBBBBB", n, n, 8, 0, 0, 0, 0)) + \
           chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def _image(grid):
    """ Write the module grid (1 = dark, 0 = light) as a grayscale PNG image, one pixel per module. """
    return _png(len(grid), b"".join(b"\x00" + bytes(0 if v else 255 for v in row) for row in grid))


def _render(grid):
    """ Write the module grid (1 = dark, 0 = light) as plain text, one character per module. """
    return "\n".join("".join(_DARK if v else _LIGHT for v in row) for row in grid)


def _read_png(data):
    """ Read a grayscale or RGB PNG image (8 bits, no interlacing) as a module grid (1 = dark, 0 = light). """
    try:
        w, h, depth, ctype = struct.unpack(">IIBB", data[16:26])
    except struct.error:
        raise FakeqrDecodeError("'fakeqr' codec can't decode malformed PNG input")
    if w != h or w not in _SIZES:
        raise FakeqrDecodeError("'fakeqr' codec can't decode input of invalid size")
    if depth != 8 or ctype not in (0, 2):
        raise FakeqrDecodeError("'fakeqr' codec can't decode input of unsupported PNG format")
    channels = {0: 1, 2: 3}[ctype]
    try:
        idat, pos = bytearray(), 8
        while pos < len(data):
            length, tag = struct.unpack(">I4s", data[pos:pos+8])
            if tag == b"IDAT":
                idat += data[pos+8:pos+8+length]
            elif tag == b"IEND":
                break
            pos += length + 12
        raw, pos, stride, grid = zlib.decompress(bytes(idat)), 0, w * channels, []
        for _ in range(h):
            if raw[pos] != 0:  # only the "None" filter is produced by this codec
                raise ValueError
            line = raw[pos+1:pos+1+stride]
            if len(line) < stride:
                raise ValueError
            grid.append([int(line[x*channels] < 128) for x in range(w)])
            pos += stride + 1
    except (IndexError, ValueError, struct.error, zlib.error):
        raise FakeqrDecodeError("'fakeqr' codec can't decode malformed PNG input")
    return grid


def _read_text(text):
    """ Read a plain text rendering (one character per module, a space being a light module) as a module grid. """
    lines = text.split("\n")
    while lines and lines[-1] == "":  # drop the trailing newline(s), if any
        lines.pop()
    n = len(lines[0]) if lines else 0  # the first row starts and ends with a finder, hence is never shortened
    if n not in _SIZES or len(lines) != n or any(len(line) > n for line in lines):
        raise FakeqrDecodeError("'fakeqr' codec can't decode input of invalid size")
    return [[int(c != _LIGHT) for c in line] + [0] * (n - len(line)) for line in lines]


def fakeqr(fmt=None, mask=None):
    txt = fmt in ("text", "txt")
    m = None if mask in (None, "") else int(mask)
    def encode(text, errors="strict"):
        data = b(text)
        bits = [int(x) for byte in struct.pack(">I", len(data)) + data for x in format(byte, "08b")]
        n = _grid_size(len(bits))
        grid, reserved, it = [[0] * n for _ in range(n)], _reserved(n), iter(bits)
        for r in range(n):
            for c in range(n):
                if (r, c) in reserved:
                    continue
                v = next(it, 0)
                grid[r][c] = v ^ 1 if m is not None and _MASKS[m](r, c) else v
        _decorate(grid, n)
        return (_render(grid) if txt else _image(grid)), len(text)
    def decode(text, errors="strict"):
        data = b(text)
        grid = _read_png(data) if data[:8] == _SIGNATURE else _read_text(text)
        n, bits, reserved = len(grid), [], _reserved(len(grid))
        for r in range(n):
            for c in range(n):
                if (r, c) in reserved:
                    continue
                v = grid[r][c]
                bits.append(v ^ 1 if m is not None and _MASKS[m](r, c) else v)
        length = int("".join(map(str, bits[:32])), 2)
        bits = bits[32:32+8*length]
        if len(bits) < 8 * length:
            raise FakeqrDecodeError("'fakeqr' codec can't decode malformed input")
        out = bytes(int("".join(map(str, bits[i:i+8])), 2) for i in range(0, 8 * length, 8))
        return ensure_str(out), length
    return encode, decode


def fakeqr_encode(fmt=None, mask=None):
    return fakeqr(fmt, mask)[0]


def fakeqr_decode(fmt=None, mask=None):
    return fakeqr(fmt, mask)[1]


# a valid 21x21 image (decoding to the empty string), used to derive malformed inputs for the decoding examples
_VALID = _image([[0] * 21 for _ in range(21)])
__examples__ = {
    'enc(fakeqr)': {'x' * 4000: None},
    'dec(fakeqr)': {
        "\x89PNG\r\n\x1a\n":                               None,  # truncated PNG header
        "not a fake QR code":                             None,  # not a valid text grid
        "":                                               None,  # empty input
        _image([[0] * 10 for _ in range(10)]):            None,  # PNG size that is not a QR version
        _VALID[:25] + b"\x03" + _VALID[26:]:              None,  # unsupported color type (palette)
        _png(21, b"\x01" + bytes(21)):                    None,  # unsupported scanline filter
        _png(21, b"\x00" + bytes(5)):                     None,  # truncated scanline
        _image([[1] * 21 for _ in range(21)]):            None,  # length header larger than the data
    },
    'enc-dec(fakeqr|fake-qr|fakeqr-0|fakeqr-5|fake_qr_7|fakeqr-text|fakeqr-txt|fake_qr_text_3)': [
        "", "this is a test", "Hello, World! 123", "\xe9t\xe9 \xff", "".join(chr(i) for i in range(256))],
}
__guess__ = ["fakeqr"]


add("fakeqr", fakeqr_encode, fakeqr_decode, r"^fake[-_]?qr(?:[-_](text|txt))?(?:[-_]([0-7]))?$", guess=__guess__,
    expansion_factor=None)
