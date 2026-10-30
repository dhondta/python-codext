# -*- coding: UTF-8 -*-
"""Helpers for the codecs generating JavaScript (aaencode, jjencode).

"""
import re


__all__ = ["js_unescape", "utf16_units"]


ESCAPES = {'b': "\b", 'f': "\f", 'n': "\n", 'r': "\r", 't': "\t", 'v': "\v"}


def js_unescape(s, err):
    """ Evaluate the body of a JavaScript double-quoted string literal (in sloppy mode, thus with legacy octal escapes),
         calling err with a message on a syntax error. UTF-16 surrogate pairs are combined into characters. """
    r, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c != "\\":
            if c in "\"\r\n":
                err(f"unescaped {c!r} in string literal")
            r.append(c)
            i += 1
            continue
        if i + 1 >= n:
            err("unterminated escape sequence in string literal")
        e, i = s[i+1], i + 2
        if e in ESCAPES:
            r.append(ESCAPES[e])
        elif e in "\r\n  ":
            # line continuation
            i += e == "\r" and s.startswith("\n", i)
        elif e in "01234567":
            # legacy octal escape: up to \377
            m = re.match(r"[0-7]{0,2}" if e in "0123" else r"[0-7]?", s[i:])
            r.append(chr(int(e + m.group(), 8)))
            i += m.end()
        elif e == "x":
            if not re.fullmatch(r"[0-9a-fA-F]{2}", s[i:i+2]):
                err("invalid hexadecimal escape sequence")
            r.append(chr(int(s[i:i+2], 16)))
            i += 2
        elif e == "u":
            if (m := re.match(r"\{([0-9a-fA-F]+)\}|[0-9a-fA-F]{4}", s[i:])) is None or \
               int(m.group(1) or m.group(), 16) > 0x10ffff:
                err("invalid Unicode escape sequence")
            r.append(chr(int(m.group(1) or m.group(), 16)))
            i += m.end()
        else:
            # including "8" and "9"
            r.append(e)
    return "".join(r).encode("utf-16-le", "surrogatepass").decode("utf-16-le", "surrogatepass")


def utf16_units(text):
    """ Get the UTF-16 code units of a string, as with JavaScript's charCodeAt. """
    b = text.encode("utf-16-le", "surrogatepass")
    return [int.from_bytes(b[i:i+2], "little") for i in range(0, len(b), 2)]
