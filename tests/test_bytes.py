#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Bytes handling tests, generated for every codec.

Each codec declares the kind of its plain side (what is encoded) and of its encoded side: "bytes" (data, handled byte
 for byte) or "text" (characters, read from and written to bytes as UTF-8). Hence:
- consistency: a bytes input gives the same result as the equivalent str input, in the form of each side (UTF-8 for a
   text side, byte for byte for a bytes side), when encoding as when decoding ;
- exactness: with a bytes plain side, any bytes that the codec accepts are recovered exactly after encoding and decoding
   (including bytes that happen to be valid UTF-8).
"""
import random
import re
from unittest import TestCase

from codext.__common__ import *


TEXTS = ["Hello, World!", "café ça", "naïve résumé", "日本語 ok", "\x01\x7f tab\t"]
DATA = [b"8\xc2\xb96", "café ça".encode(), bytes(range(256)), random.Random(0).randbytes(64)]


def _form(x, side):
    """ Bytes form of a value on the given side of a codec: UTF-8 on a text side, byte for byte on a bytes side. """
    if not isinstance(x, str):
        return x
    return x.encode("utf-8") if side == "text" else b(x)


def _forms(x, side):
    """ Possible bytes forms of a value given by the str path ; on a bytes side, as the str path gives bytes either as
         they are (in Latin-1) or read as UTF-8 (when a codec returns bytes), both are possible. """
    if not isinstance(x, str):
        return [x]
    return [x.encode("utf-8")] if side == "text" else list({b(x), x.encode("utf-8")})


def _names(params):
    """ Encoding names to be tested for a codec: some of its guessed encodings and of the names of its examples. """
    names = list(params.get('guess') or [])[:3]
    for k in (params.get('examples') or {}):
        m = re.match(r"(?:dec|enc|enc-dec)\((.*?)\)", k)
        if m:
            names.extend(m.group(1).split("|")[:2])
    r = []
    for n in names + [params['name']]:
        try:
            lookup(n)
        except LookupError:
            continue
        if n not in r:
            r.append(n)
    return r[:4]


def make_test(params):
    def _template(self):
        for name in _names(params):
            # the kinds of the sides may depend on the encoding name
            plain, encoded = lookup(name).parameters['plain'], lookup(name).parameters['encoded']
            # consistency between the str and bytes paths, in both directions
            for s in TEXTS:
                try:
                    e = encode(s, name)
                except Exception:
                    continue
                # a non-deterministic encoding (e.g. a salted hash) cannot be compared
                if e == encode(s, name):
                    with self.subTest(encoding=name, text=s, direction="encode"):
                        self.assertIn(_form(encode(_form(s, plain), name), encoded), _forms(e, encoded))
                try:
                    d = decode(e, name)
                except Exception:
                    continue
                with self.subTest(encoding=name, text=s, direction="decode"):
                    self.assertIn(_form(decode(_form(e, encoded), name), plain), _forms(d, plain))
            # exactness of the bytes recovered with a bytes plain side
            if plain != "bytes":
                continue
            for data in DATA:
                try:
                    e = encode(data, name)
                except Exception:
                    continue
                with self.subTest(encoding=name, data=data[:16], direction="round-trip"):
                    try:
                        d = decode(e, name)
                    except NotImplementedError:
                        break  # e.g. a hash
                    self.assertEqual(d if isinstance(d, bytes) else b(d), data)
    return _template


class BytesTestCase(TestCase):
    def test_text_to_text_not_utf8(self):
        # input that is not valid UTF-8 is given back in the form it was read (Latin-1), not converted to UTF-8
        for name, data, output in [("rot13", b"caf\xe9", b"pns\xe9"), ("reverse", b"caf\xe9", b"\xe9fac"),
                                   ("swapcase", b"caf\xe9", b"CAF\xc9"), ("rot13", b"\xff\x00abc", b"\xff\x00nop")]:
            with self.subTest(encoding=name, data=data):
                self.assertEqual(encode(data, name), output)
                self.assertEqual(decode(output, name), data)

    def test_text_to_text_utf8(self):
        # valid UTF-8 stays UTF-8, as bytes or as the equivalent str
        self.assertEqual(encode("café".encode(), "rot13"), "pnsé".encode())
        self.assertEqual(decode("pnsé".encode(), "rot13"), "café".encode())
        self.assertEqual(encode("café", "rot13"), "pnsé")
        self.assertEqual(encode("é\xe9".encode(), "reverse"), "\xe9é".encode())

    def test_text_to_text_not_utf8_ascii_output(self):
        # known limit: the decoder only sees ASCII and has no way to know that the input was not valid UTF-8
        for name, output in [("url", b"%E9"), ("html", b"&eacute;")]:
            with self.subTest(encoding=name):
                self.assertEqual(encode(b"\xe9", name), output)
                self.assertEqual(decode(output, name), "é".encode())

    def test_text_to_text_not_utf8_utf8_output(self):
        # known limit: the output happens to be valid UTF-8, hence the decoder reads it as such
        self.assertEqual(encode(b"\xa9\xc3", "reverse"), b"\xc3\xa9")
        self.assertEqual(decode(b"\xc3\xa9", "reverse"), b"\xc3\xa9")


for encoding in list_encodings():
    try:
        ci = lookup(encoding, False)
    except LookupError:
        continue
    if ci.parameters.get('category') == "native" or 'plain' not in ci.parameters:
        continue
    f = make_test(ci.parameters)
    f.__name__ = n = "test_bytes_" + encoding.replace("-", "_")
    setattr(BytesTestCase, n, f)
