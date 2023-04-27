# -*- coding: UTF-8 -*-
"""Base85 Codec - base85 content encoding.

This is a simple wrapper for adding base64.b85**code to the codecs.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)
"""
import base64

from ._base import _get_charset, digits, lower, main, upper
from ..__common__ import *


__examples__ = {
    'enc-dec(base85|z85|base85-ipv6)':   ["@random{512,1024,2048}"],
    'enc-dec(base85-btoa|base85-xbtoa)': ["@random{512,1024,2048}"],
    'enc(base85|ascii85)':               {'this is a test': "FD,B0+DGm>@3BZ'F*%"},
    'enc(base85-adobe)':                 {'this is a test': "<~FD,B0+DGm>@3BZ'F*%~>",
                                          'this is a test\0\0\0\0\0\0': "<~FD,B0+DGm>@3BZ'F*%B^z~>"},
    'enc(z85|base85-z)':                 {'this is a test': "BzbxfazC)tvixV6B94"},
    'enc(base85-ipv6|base85_rfc1924)':   {'this is a test': "bZBXFAZc?TVIXv6b94"},
    'enc(base85_btoa)':                  {'this is a test': "FD,B0+DGm>@3BZ'F*%B^"},
    'enc(base85_btoa)':                  {'this\0\0\0\0test': "FD,B0+DGm>@3BZ'F*%B^"},
    'enc(base85_btoa)':                  {'this is     a test\0\0\0\0': "FD,B0+DGm>y@3BZ'F*%B^z"},
    'enc(base85-xbtoa)':                 {'this is a test': "xbtoa Begin\nFD,B0+DGm>@3BZ'F*%B^\nxbtoa End N 14 e E 4b" \
                                                            " S 523 R 1b132e"},
    'dec(base85-xbtoa)':                 {'xbtoa Begin\nFD,B0+DGm>@3BZ\'F*%B^\nxbtoa End': None,
                                          'xbtoa Begin\nFD,B0+DGm>@3BZ\'F*%B^\nxbtoa End N 14 e E 4b S 523 R 000bad':
                                          None},
    'enc(base85-xml)':                   {'this is a test': "bZBXFAZc@TVIXv6b94"},
    'enc(base85|ascii85)':               {'this\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0test': "FD,B0zzz!!!\"@ATMq"},
}
__guess__ = ["ascii85", "z85", "base85-ipv6", "base85-xml", "base85-adobe", "base85-xbtoa"]


B85 = {
    r'(base[-_]?85([-_]ascii)?|ascii85)$': "!\"#$%&'()*+,-./" + digits + ":;<=>?@" + upper + "[\\]^_`" + lower[:21],
    r'(z85|base[-_]?85[-_]z(eromq)?)$':    digits + lower + upper + ".-:+=^!/*?&<>()[]{}@%$#",
    r'base[-_]?85[-_](rfc1924|ipv6)$':     digits + upper + lower + "!#$%&()*+-;<=>?@^_`{|}~",
    r'base[-_]?85[-_]xml$':                digits + upper + lower[:-1] + "!#$()*+,-./:;=?@^`{|}~z_",
}
B85[r'(base[-_]?85[-_]adobe)$'] = B85[r'(base[-_]?85[-_]x?btoa)$'] = B85[r'(base[-_]?85([-_]ascii)?|ascii85)$']
POW85 = [85 ** i for i in range(5)]


def __format(text, mode, decode=False, **kwargs):
    if "adobe" in mode:
        if decode:
            if text.startswith("<~") and text.endswith("~>"):
                text = text[2:-2]
        else:
            text = "<~" + text + "~>"
    elif "xbtoa" in mode:
        sp, ep = "xbtoa [bB]egin\n", "xbtoa [eE]nd"
        if decode:
            if re.match(r"^xbtoa\s+[bB]egin\n", text) and \
               re.search(r"\nxbtoa\s+[eE]nd N \d+{h} E{h} S{h} R{h}\s*$".format(h=" [0-9a-fA-F]+"), text):
                text = "".join(text.split("\n")[1:-1]).replace(" ", "")
        elif not decode:
            l, t = kwargs['length'], "\n".join(text[i:i+78] for i in range(0, len(text), 78))
            text = "xbtoa Begin\n%s\nxbtoa End N %d %x E %x S %x R %x" % \
                   (t, l, l, kwargs['c_xor'], kwargs['c_sum'], kwargs['c_rot'])
    return text


def __xbtoa_values(text):
    try:
        hr = "[0-9a-fA-F]+"
        return re.search(r"\nxbtoa\s+[eE]nd N (\d+) ({h}) E ({h}) S ({h}) R ({h})\s*$".format(h=hr), text).groups()
    except:
        raise Base85DecodeError("Bad or missing xbtoa parameters")


def base85_encode(mode):
    b85 = _get_charset(B85, mode)
    def encode(input, errors="strict"):
        r, l, kw = "", len(input), {}
        if l == 0:
            return input, 0
        if "xbtoa" in mode:
            kw['length'] = l
            kw['c_xor'], kw['c_sum'], kw['c_rot'] = 0, 0, 0
        n_pad = (4 - l % 4) % 4
        for i in range(0, l, 4):
            block = input[i:i+4]
            if block == "\0\0\0\0" and b85[-3:] == "stu":
                r += "z"
            if block == "\x20\x20\x20\x20" and "btoa" in mode:
                r += "y"
            if "xbtoa" in mode:
                for c in block:
                    k = ord(c)
                    kw['c_xor'] ^= k
                    kw['c_sum'] += k + 1
                    kw['c_rot'] <<= 1
                    if kw['c_rot'] & 0x80000000:
                        kw['c_rot'] += 1
                    kw['c_rot'] += k
            if block == "\0\0\0\0" and b85[-3:] == "stu" or block == "\x20\x20\x20\x20" and "btoa" in mode:
                continue
            if len(block) < 4:
                block += n_pad * "\0"
            n, bl = s2i(block), ""
            for _ in range(5):
                n, k = divmod(n, 85)
                bl = b85[k] + bl
            r += bl
        if "btoa" not in mode and n_pad:
            r = r[:-n_pad]
        if b85[-3:] == "stu" and r[-5:] == "!!!!!":
            r = r[:-5] + "z"
        return __format(r, mode, **kw), l
    return encode


def base85_decode(mode):
    b85 = _get_charset(B85, mode)
    def decode(input, errors="strict"):
        r, l, i, n_pad = "", len(input), 0, 0
        if l == 0:
            return input, 0
        if "xbtoa" in mode:
            v = __xbtoa_values(input)
            n_last = int(v[0]) % 4
            c_xor, c_sum, c_rot = 0, 0, 0
        input = __format(input, mode, True)
        ehandler = handle_error("base85", errors, decode=True)
        if b85[-3:] == "stu" and input[-1] == "z":
            input = input[:-1] + "!!!!!"
        l = len(input)
        while i < l:
            n, incr = 0, 5
            if input[i] == "z" and b85[-3:] == "stu":
                bl, incr = "\0\0\0\0", 1
            elif input[i] == "y" and "btoa" in mode:
                bl, incr = "\x20\x20\x20\x20", 1
            else:
                block = input[i:i+5]
                if len(block) < 5:
                    n_pad = 5 - len(block) % 5
                    block += n_pad * "\0"
            for k, c in enumerate(block[::-1]):
                try:
                    n += (b85.index(c) if c != "\0" else 255) * POW85[k]
                except ValueError:
                    r += ehandler(c, i + k, r)
            bl = codecs.decode("{:0>8}".format(hex(n & 0xffffffff)[2:]), "hex")
            if "xbtoa" in mode:
                if i + 5 == l and n_last > 0:
                    bl = bl[:n_last]
                for c in bl:
                    k = ord(c)
                    c_xor ^= k
                    c_sum += k + 1
                    c_rot <<= 1
                    if c_rot & 0x80000000:
                        c_rot += 1
                    c_rot += k
            r += bl
            i += incr
        if n_pad > 0:
            r = r[:-n_pad]
        if "xbtoa" in mode:
            chkv = ["%d" % len(r), "%x" % len(r), "%x" % c_xor, "%x" % c_sum, "%x" % c_rot]
            if any(v1 != v2 for v1, v2 in zip(v, chkv)) and errors == "strict":
                raise Base85ValueError("A check value does not match (%s != %s)" % (str(list(v)).replace("'", ""),
                                                                                    str(chkv).replace("'", "")))
        return r, l
    return decode


add("base85", base85_encode, base85_decode, expansion_factor=lambda f, ename: f if "xbtoa" in ename else 1.25,
    pattern=r"^(base[-_]?85(?:|[-_](?:adobe|x?btoa|ipv6|rfc1924|xml|z(?:eromq)?))|z85|ascii85)$",
    extra_exceptions=["Base85ValueError"])
main85        = main(85, None)
main85adobe   = main(85, None, "adobe")
main85xbtoa   = main(85, None, "xbtoa", wrap=False)
main85rfc1924 = main(85, "RFC 1924", "ipv6")
main85xml     = main(85, "<https://datatracker.ietf.org/doc/html/draft-kwiatkowski-base85-for-xml-00>", "xml")
main85zeromq  = main(85, "<https://rfc.zeromq.org/spec/32/>", "zeromq")

