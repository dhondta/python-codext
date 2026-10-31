# -*- coding: UTF-8 -*-
"""Huffman Codec - Huffman coding content compression.

Huffman coding, devised by David A. Huffman in 1952, gives the frequent symbols shorter codes than the rare ones, with
 an optimal prefix code (no code being the beginning of another) built by merging the two least frequent groups of
 symbols until a single one remains. This codec builds the code of the bytes of the text and writes it as a canonical
 Huffman code (the codes being assigned in order of length, then of symbol, hence given by their lengths only), in a
 self-describing format:
- the number of distinct bytes minus 1 (1 byte)
- for each of them, the byte and the length of its code (2 bytes)
- the number of padding bits at the end of the last byte (1 byte)
- the codes of the bytes of the text, from the most significant bit (a single distinct byte having the code "0")

An empty text gives an empty output. As with the other compression codecs, malformed data is reported (or, with a
 non-strict errors handling, replaced, dropped or left as is), but, as the length of the text is not stored, data
 truncated at the end of a code gives a truncated text.

NB: Not an encoding properly speaking.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Canonical_Huffman_code
"""
import heapq
from collections import Counter

from ..__common__ import *


__examples__ = {
    'enc(huffman)': {'': "", 'a': "\x00a\x01\x07\x00", 'aab': "\x01a\x01b\x01\x05 ",
                     'abracadabra': "\x04a\x01b\x03c\x03d\x03r\x03\x01N\xac\x9c"},
    'dec(huffman)': {'\x00a\x01\x07\x00': "a", '\x01a\x01b\x01\x05 ': "aab", '\x01a\x01a\x01\x05 ': None,
                     '\x01a\x01b\x02\x05 ': None, '\x01a\x01b\x01\x08 ': None, '\x01a\x01b\x01': None,
                     '\x05': None, '\x01a\x01b\x00\x05 ': None, '\x00a\x02\x07\x00': None},
    'enc-dec(huffman)': ["", "aaaa", "This is a test", "@random{1,256,2048}"],
}


def _lengths(data):
    """ Lengths of the Huffman codes of the bytes of the data, merging the least frequent groups (the ties being broken
         by the order of creation, the bytes being taken in increasing order). """
    counts = Counter(data)
    if len(counts) == 1:
        return {next(iter(counts)): 1}
    heap, lengths = [(n, i, [s]) for i, (s, n) in enumerate(sorted(counts.items()))], dict.fromkeys(counts, 0)
    heapq.heapify(heap)
    i = len(heap)
    while len(heap) > 1:
        n1, _, g1 = heapq.heappop(heap)
        n2, _, g2 = heapq.heappop(heap)
        for s in g1 + g2:
            lengths[s] += 1
        heapq.heappush(heap, (n1 + n2, i, g1 + g2))
        i += 1
    return lengths


def _canonical(lengths):
    """ Canonical codes (as (code, length)) of the bytes, assigned in order of length, then of byte. """
    codes, code, prev = {}, 0, 0
    for s, n in sorted(lengths.items(), key=lambda x: (x[1], x[0])):
        code <<= n - prev
        codes[s], code, prev = (code, n), code + 1, n
    return codes


def huffman_compress(text, errors="strict"):
    data = b(ensure_str(text))
    if not data:
        return b"", len(text)
    lengths = _lengths(data)
    codes, header = _canonical(lengths), bytes([len(lengths) - 1])
    for s in sorted(lengths):
        header += bytes([s, lengths[s]])
    acc, nbits = 0, 0
    for x in data:
        c, n = codes[x]
        acc, nbits = acc << n | c, nbits + n
    pad = -nbits % 8
    # the compressed data is given as latin-1 text (or bytes), so that it is read back as is
    return (header + bytes([pad]) + (acc << pad).to_bytes((nbits + pad) // 8, "big")).decode("latin-1"), len(text)


def _error(msg):
    raise HuffmanDecodeError(f"'huffman' codec can't decode: {msg}")


def _decode(data):
    """ Decode Huffman-coded data, raising an error with a precise message if it is malformed. """
    if not data:
        return b""
    n = data[0] + 1
    if len(data) < 2 + 2 * n:
        _error("truncated header")
    lengths = {}
    for i in range(n):
        s, length = data[1 + 2 * i], data[2 + 2 * i]
        if s in lengths or length == 0:
            _error("bad code length" if length == 0 else f"duplicate byte {s}")
        lengths[s] = length
    # the code lengths must give a complete prefix code (Kraft's equality), a single byte having a code of 1 bit
    m = max(lengths.values())
    if (sum(1 << (m - length) for length in lengths.values()) != 1 << m) if n > 1 else m != 1:
        _error("code lengths not giving a complete prefix code")
    pad, payload = data[1 + 2 * n], data[2 + 2 * n:]
    if pad > 7 or not payload or 8 * len(payload) - pad < min(lengths.values()):
        _error("bad padding")
    table = {(c, l): s for s, (c, l) in _canonical(lengths).items()}
    bits, r, code, length = int.from_bytes(payload, "big") >> pad, bytearray(), 0, 0
    # as the code is complete, any sequence of bits is a sequence of codes, possibly followed by a truncated one
    for i in range(8 * len(payload) - pad - 1, -1, -1):
        code, length = code << 1 | bits >> i & 1, length + 1
        if (code, length) in table:
            r.append(table[code, length])
            code, length = 0, 0
    if length:
        _error("truncated code at the end")
    return bytes(r)


def huffman_decompress(text, errors="strict"):
    data = b(ensure_str(text))
    try:
        return _decode(data), len(text)
    except HuffmanDecodeError:
        # as with gzip and zstd, malformed data is reported (with a precise message), or replaced, dropped or left as is
        if errors == "strict":
            raise
        return handle_error("huffman", errors, decode=True)(data[:1].decode("latin-1"), 0), len(text)


add("huffman", huffman_compress, huffman_decompress, guess=None)
