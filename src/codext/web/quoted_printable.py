# -*- coding: UTF-8 -*-
"""Quoted-Printable Codec - quoted-printable content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://en.wikipedia.org/wiki/Quoted-printable
"""
import quopri

from ..__common__ import *


__examples__ = {
    'enc(quoted-printable|qp|quopri)': {'Subject: =?UTF-8?': "Subject: =3D?UTF-8?"},
}
__guess__ = ["quoted-printable"]


def qp_encode(text, errors="strict"):
    t = ensure_str(text)
    r = quopri.encodestring(t.encode("latin-1", errors=errors)).decode("ascii")
    return r, len(t)


def qp_decode(text, errors="strict"):
    t = ensure_str(text)
    r = quopri.decodestring(t.encode("ascii")).decode("latin-1")
    return r, len(t)


add("quoted-printable", qp_encode, qp_decode,
    r"^(?:quoted[-_]printable|qp|quopri)$",
    examples=__examples__, guess=__guess__, expansion_factor=(1.1, .1), printables_rate=1.)
