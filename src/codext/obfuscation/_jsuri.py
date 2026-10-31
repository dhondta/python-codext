# -*- coding: UTF-8 -*-
"""URI encoding, shared by the toy encodings of online JavaScript encryption tools that substitute the characters of the
 text encoded with JavaScript's encodeURIComponent() (ARABICA-2RS, CHINZO-72C, HINDIA-4X, JAPOO-C2S, KOREX-3S).

The text is encoded like encodeURIComponent() does (the UTF-8 bytes of the characters other than the letters, digits
 and "-_.!~*'()" being written as "%XX"), hence it is made of 72 distinct characters, each one being substituted by a
 character (or a short string) of the encoding ; decoding substitutes them back and decodes the text like
 decodeURIComponent() does, malformed escape sequences and invalid UTF-8 being reported (or, with a non-strict errors
 handling, replaced).
"""
import builtins
import re
from string import ascii_letters, digits
from urllib.parse import quote, unquote

from ..__common__ import ensure_str, exc_name, handle_error


# characters left as is by encodeURIComponent(), and the characters of its output
URI_SAFE = "-_.!~*'()"
URI_CHARS = ascii_letters + digits + URI_SAFE + "%"


def uri_encode(text):
    """ Encode a string like JavaScript's encodeURIComponent(). """
    return quote(ensure_str(text), safe=URI_SAFE)


def uri_decode(text, ename, errors="strict"):
    """ Decode a string like JavaScript's decodeURIComponent(), with the given errors handling. """
    if errors == "strict":
        if (m := re.search(r"%(?![0-9A-Fa-f]{2})", text)):
            handle_error(ename, errors, decode=True, kind="escape sequence")(text[m.start():m.start()+3], m.start())
        try:
            return unquote(text, errors="strict")
        except UnicodeDecodeError as e:
            exc = getattr(builtins, f"{exc_name(ename)}DecodeError")
            raise exc(f"'{ename}' codec can't decode: invalid UTF-8 ({e.reason})") from None
    # with a non-strict errors handling, malformed escape sequences are kept as is and invalid UTF-8 is replaced
    return unquote(text, errors="replace")


def substitution(ename, table, decode_table=None):
    """ Make the encoding and decoding functions of an encoding substituting the characters of the URI-encoded text,
         given the substitutes of these characters. """
    dtable = decode_table or {v: k for k, v in table.items()}

    def encode(text):
        return [table[c] for c in uri_encode(text)]

    def decode(tokens, errors="strict"):
        _h = handle_error(ename, errors, decode=True)
        return uri_decode("".join(dtable[t] if t in dtable else _h(t, i) for i, t in enumerate(tokens)), ename, errors)

    return encode, decode
