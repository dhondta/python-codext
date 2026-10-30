# -*- coding: UTF-8 -*-
"""ATOM-128 Codec - ATOM-128 content encoding.

ATOM-128 is a toy cipher found on online JavaScript encryption tools. It is Base64 with a shuffled alphabet, whose 65th
 character ("C") is used for padding. As in the original JavaScript, the text is first escaped with JavaScript's
 escape() (e.g. " " becoming "%20" and "é" becoming "%E9"), and unescaped after decoding ; ciphertexts made without this
 escaping (i.e. from the UTF-8 bytes of the text) are then decoded the same way.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://github.com/gungunfebrianza/Mastering-Cryptography/blob/master/ATOM-128/ATOM-128.js
"""
import re
from base64 import b64decode, b64encode
from binascii import Error as B64Error
from string import ascii_letters, ascii_lowercase as LC, ascii_uppercase as UC, digits

from ..__common__ import *


__examples__ = {
    'enc(atom128|atom-128|atom_128)': {'this is a test': "0IXBnsgsSI6tQfPqKDgsSoA6nmbC", 'test': "0IHt0/CC", '': ""},
    'dec(atom128)': {'0IHt0/CC': "test", '0IHt 0/CC': "test", '0IHt0/C': None, '0IHt0/C%': None},
    'enc-dec(atom128)': ["this is a test", "Hello, World! 1234", "\xe9t\xe9 \u2603 \U0001F600", "100% sure", "a"],
}
__guess__ = ["atom128"]


B64 = UC + LC + digits + "+/="
ATOM128 = "/128GhIoPQROSTeUbADfgHijKLM+n0pFWXY456xyzB7=39VaqrstJklmNuZvwcdEC"
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


def atom128_encode(text, errors="strict"):
    r = b64encode(js_escape(ensure_str(text)).encode()).decode()
    return r.translate(str.maketrans(B64, ATOM128)), len(text)


def atom128_decode(text, errors="strict"):
    _h, t, r = handle_error("atom128", errors, decode=True), re.sub(r"\s", "", ensure_str(text)), ""
    for i, c in enumerate(t):
        if c in ATOM128:
            r += B64[ATOM128.index(c)]
        else:
            # invalid characters are dropped (as the original JavaScript does) when not in strict mode
            _h(c, i)
    try:
        r = b64decode(r, validate=True)
    except B64Error:
        if errors == "strict":
            raise Atom128DecodeError("'atom128' codec can't decode: incorrect padding")  # noqa: F821
        # otherwise, the padding is fixed, dropping an incomplete last character
        r = r.replace("=", "")
        r = r[:len(r) - (len(r) % 4 == 1)]
        r = b64decode(r + "=" * (-len(r) % 4))
    return js_unescape(r.decode("latin-1")), len(text)


add("atom128", atom128_encode, atom128_decode, r"^atom[-_]?128$", printables_rate=1., expansion_factor=(1.6, .3))
