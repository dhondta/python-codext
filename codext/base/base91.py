# -*- coding: UTF-8 -*-
"""Base91 Codec - base91 content encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
from ._base import digits, lower, main, upper
from ..__common__ import *

# no __examples__ ; handled manually in tests/test_base.py
__guess__ = ["base91", "base91-inv", "base91-alt", "base91-alt-inv"]


B91 = {
    '':        upper + lower + digits + "!#$%&()*+,./:;<=>?@[]^_`{|}~\"",
    'inv':     lower + upper + digits + "!#$%&()*+,./:;<=>?@[]^_`{|}~\"",
    'alt':     "!#$%&'()*+,-./" + digits + ":;<=>?@" + upper + "[\\]^_" + lower + "{|}",
    'alt-inv': "!#$%&'()*+,-./" + digits + ":;<=>?@" + lower + "[\\]^_" + upper + "{|}",
}


__chr = lambda c: chr(c) if isinstance(c, int) else c
__ord = lambda c: ord(c) if not isinstance(c, int) else c


def base91_encode(mode):
    mode = mode.replace("alternate", "alt").replace("inverted", "inv").replace("_", "-").lstrip("-")
    b91 = B91[mode if mode in B91.keys() else ""]
    def encode(text, errors="strict"):
        t, s, bits = b(text), "", ""
        if mode.startswith("alt"):
            while len(bits) < 13 and t:
                bits += "{:08b}".format(__ord(t[0]))
                t = t[1:]
            while len(bits) > 13 or t:
                n = int(bits[:13], 2)
                s += b91[n // 91] + b91[n % 91]
                bits = bits[13:]
                while len(bits) < 13 and t:
                    bits += "{:08b}".format(__ord(t[0]))
                    t = t[1:]
            if len(bits) > 0:
                if len(bits) < 7:
                    bits += "0" * (6 - len(bits))
                    s += b91[int(bits, 2)]
                else:
                    bits += "0" * (13 - len(bits))
                    n = int(bits, 2)
                    s += b91[n // 91] + b91[n % 91]
        else:
            for c in t:
                bits = bin(__ord(c))[2:].zfill(8) + bits
                if len(bits) > 13:
                    n = int(bits[-13:], 2)
                    if n > 88:
                        bits = bits[:-13]
                    else:
                        n = int(bits[-14:], 2)
                        bits = bits[:-14]
                    s += b91[n % 91] + b91[n // 91]
            if len(bits) > 0:
                n = int(bits, 2)
                s += b91[n % 91]
                if len(bits) > 7 or n > 90:
                    s += b91[n // 91]
        return s, len(t)
    return encode


def base91_decode(mode):
    mode = mode.replace("alternate", "alt").replace("inverted", "inv").replace("_", "-").lstrip("-")
    b91 = {c: i for i, c in enumerate(B91[mode if mode in B91.keys() else ""])}
    def decode(text, errors="strict"):
        t, s, bits, alt = b(text), "", "", mode.startswith("alt")
        ehandler = handle_error("base91", errors, decode=True)
        for i in range(0, len(t), 2):
            try:
                n = b91[__chr(t[i])] * [1, 91][alt]
            except KeyError:
                ehandler(__chr(t[i]), i, s)
            try:
                j = i + 1
                n += b91[__chr(t[j])] * [91, 1][alt]
            except IndexError:
                pass
            except KeyError:
                ehandler(__chr(t[j]), j, s)
            if alt:
                bits += "{:013b}".format(n)
                while 8 <= len(bits):
                    s += chr(int(bits[0:8], 2))
                    bits = bits[8:]
            else:
                bits = bin(n)[2:].zfill([14, 13][n & 8191 > 88]) + bits
                while len(bits) > 8:
                    s += chr(int(bits[-8:], 2))
                    bits = bits[:-8]
        if alt and len(t) % 2 == 1:
            bits += "{:06b}".format(b91[__chr(t[-1])])
            while 8 <= len(bits):
                s += chr(int(bits[:8], 2))
                bits = bits[8:]
        elif not alt and len(bits) > 0 and not set(bits) == {"0"}:
            s += chr(int(bits, 2))
        return s, len(t)
    return decode


add("base91", base91_encode, base91_decode, r"^base[-_]?91((?:|[-_]alt(?:ernate)?)(?:|[-_]inv(?:erted)?)?)$",
    entropy=6.5, expansion_factor=1.231)
main = main(91, "<http://base91.sourceforge.net/>")

