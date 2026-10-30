# -*- coding: UTF-8 -*-
"""Base64 variants, shared by the toy ciphers of online JavaScript encryption tools (ATOM-128, ESAB-46, FERON-74).

These ciphers are Base64 with a shuffled alphabet of 65 characters, whose last one is used for padding. As in the
 original JavaScript, the text is first escaped with JavaScript's escape() (e.g. " " becoming "%20" and "é" becoming
 "%E9"), and unescaped after decoding ; ciphertexts made without this escaping (i.e. from the UTF-8 bytes of the text)
 are then decoded the same way.
"""
import builtins
import re
from base64 import b64decode, b64encode
from binascii import Error as B64Error
from string import ascii_letters, ascii_lowercase as LC, ascii_uppercase as UC, digits

from ..__common__ import ensure_str, exc_name, handle_error


B64 = UC + LC + digits + "+/="
# characters left as is by JavaScript's escape()
_SAFE = set(ascii_letters + digits + "@*_+-./")


def js_escape(text):
    """ Escape a string like JavaScript's escape() (characters beyond the BMP being escaped as surrogate pairs). """
    r = ""
    for c in text:
        if c in _SAFE:
            r += c
        elif ord(c) < 256:
            r += f"%{ord(c):02X}"
        else:
            u = c.encode("utf-16-be", "surrogatepass")
            r += "".join(f"%u{u[i:i+2].hex().upper()}" for i in range(0, len(u), 2))
    return r


def js_unescape(text):
    """ Unescape a string like JavaScript's unescape() (surrogate pairs being joined). """
    s = re.sub(r"%u([0-9a-fA-F]{4})|%([0-9a-fA-F]{2})", lambda m: chr(int(m.group(1) or m.group(2), 16)), text)
    return s.encode("utf-16-be", "surrogatepass").decode("utf-16-be", "replace")


def js_base64(name, alphabet):
    """ Make the encoding and decoding functions of a Base64 variant, given its alphabet (with the padding character
         last). """
    enc_map = str.maketrans(B64, alphabet)

    def encode(text, errors="strict"):
        return b64encode(js_escape(ensure_str(text)).encode()).decode().translate(enc_map), len(text)

    def decode(text, errors="strict"):
        _h, t, r = handle_error(name, errors, decode=True), re.sub(r"\s", "", ensure_str(text)), ""
        for i, c in enumerate(t):
            if c in alphabet:
                r += B64[alphabet.index(c)]
            else:
                # invalid characters are dropped (as the original JavaScript does) when not in strict mode
                _h(c, i)
        try:
            r = b64decode(r, validate=True)
        except B64Error:
            if errors == "strict":
                raise getattr(builtins, f"{exc_name(name)}DecodeError")(f"'{name}' codec can't decode: incorrect "
                                                                         "padding")
            # otherwise, the padding is fixed, dropping an incomplete last character
            r = r.replace("=", "")
            r = r[:len(r) - (len(r) % 4 == 1)]
            r = b64decode(r + "=" * (-len(r) % 4))
        return js_unescape(r.decode("latin-1")), len(text)

    return encode, decode
