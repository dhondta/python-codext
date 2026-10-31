# -*- coding: UTF-8 -*-
"""NS3 Codec - ZyXEL NDMS V2 password scrambling.

NS3, also called NDMS V2 or ZyXEL config, is the reversible password scrambling used in the running-config files of
 ZyXEL routers (e.g. "authentication password ns3 9IpS3eYkkEN3Vld3CXRZtnBz"). The password is padded to 18, 36 or 72
 bytes (the filler being derived from its MD5 digest), scrambled with two keystream passes keyed by the first two bytes
 of this digest, and these two key bytes are then interleaved into the result at positions depending on their value ;
 the whole is encoded with Base64. Decoding extracts the two key bytes, reverses the scrambling and strips the padding.
 Passwords of more than 69 bytes cannot be encoded.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://miloserdov.org/?p=6850
"""
from base64 import b64decode, b64encode
from hashlib import md5

from ..__common__ import *


__examples__ = {
    'enc(ns3)':     {'HackWare': "HfNV/Uq8ubal+UXhXERgHRdO", 'x' * 70: None},
    'dec(ns3)':     {'HfNV/Uq8ubal+UXhXERgHRdO': "HackWare", '9IpS3eYkkEN3Vld3CXRZtnBz': "Miloserdov",
                     'Zm9v': None, 'not base64 !': None, 'aV+3zYmsIObym3qal16P3r3n': None},
    'enc-dec(ns3)': ["", "this is a test", "Hello, World!", "\xe9t\xe9", "x" * 69],
}
__guess__ = ["ns3"]


def _first_step(data, x1, x2):
    # XOR each byte with a Fibonacci-like keystream (mod 256) seeded by the two key bytes ; its own inverse
    x1, x2 = x1 & 0xff, x2 & 0xff
    for i in range(len(data)):
        data[i] = (data[i] ^ x2) & 0xff
        x2, x1 = (x1 + x2) & 0xff, x2
    return data


def _second_step(data):
    # XOR every byte with a value derived from the XOR of all the bytes ; its own inverse when the count is even
    x = 0
    for b in data:
        x ^= b
    for i in range(1, 8):
        a = ((x >> i) ^ (~x << i)) & 0xff
        x = ((a << i) ^ (~a ^ x)) & 0xff
    for i in range(len(data)):
        data[i] ^= x
    return data


def ns3_encode(text, errors="strict"):
    data = b(ensure_str(text))
    old_length, n = len(data), len(data) + 3
    length = 0x12 if n < 0x13 else 0x24 if n < 0x25 else 0x48 if n < 0x49 else None
    if length is None:
        raise ValueError("'ns3' codec can't encode input of more than 69 bytes")
    digest, data = md5(data).digest(), list(data)
    data.append(0)
    for i in range(old_length + 1, length - 2):
        data.append((data[i-old_length-1] * 2 + digest[2+i%14]) & 0xff)
    x1, x2 = digest[0], digest[1]
    data = _second_step(_first_step(data, x1, x2))
    data.insert(x2 % (length - 1), x1)
    data.insert(length // 7, x2)
    return b64encode(bytes(data)).decode(), len(text)


def ns3_decode(text, errors="strict"):
    s = ensure_str(text)
    s += "=" * (-len(s) % 4)
    try:
        data = list(b64decode(s, validate=True))
    except Exception:
        raise ValueError("'ns3' codec can't decode invalid Base64 input")
    length = len(data)
    if length not in (0x12, 0x24, 0x48):
        raise ValueError("'ns3' codec can't decode input of invalid length")
    x2 = data.pop(length // 7)
    x1 = data.pop(x2 % (length - 1))
    data = _first_step(_second_step(data), x1, x2)
    try:
        end = data.index(0)
    except ValueError:
        raise ValueError("'ns3' codec can't decode malformed input")
    return ensure_str(bytes(data[:end])), len(text)


add("ns3", ns3_encode, ns3_decode, pattern=r"^ns3$", entropy=6., printables_rate=1.)
