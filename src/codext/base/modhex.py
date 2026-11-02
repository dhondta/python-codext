# -*- coding: UTF-8 -*-
"""ModHex Codec - modified hexadecimal content encoding.

ModHex (modified hexadecimal) is the hexadecimal encoding used by YubiKeys for their one-time passwords: the digits 0 to
 f are replaced by the letters "cbdefghijklnrtuv", which are at the same positions on most keyboard layouts, as a
 YubiKey types its output as a USB keyboard. Encoding gives the digits without delimiter (as typed by a YubiKey), while
 decoding ignores the case, whitespaces and the delimiters "%", ",", ";" and ":" (as output by CyberChef).

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://developers.yubico.com/yubico-c/Manuals/modhex.1.html
"""
from ..__common__ import *


__examples__ = {
    'enc(modhex|mod-hex|mod_hex|base16-modhex|yubikey-modhex)': {'\n\x14\x1e': "clbfbu", 'test': "ifhgieif", '': ""},
    'dec(modhex)': {'clbfbu': "\n\x14\x1e", 'cl bf bu': "\n\x14\x1e", 'CL:BF:BU': "\n\x14\x1e", 'cl\r\nbf': "\n\x14",
                    'cla': None, 'clb': None, 'clxx': None},
    'enc-dec(modhex)': ["test", "This is a test", "@random{512,1024,2048}"],
}
__guess__ = ["modhex"]


MODHEX, HEX = "cbdefghijklnrtuv", "0123456789abcdef"
_ENC, _DEC = str.maketrans(HEX, MODHEX), {c: h for c, h in zip(MODHEX, HEX)}
DELIMITERS = " \t\r\n%,;:"


def modhex_encode(text, errors="strict"):
    t = b(text)
    return t.hex().translate(_ENC), len(t)


def modhex_decode(text, errors="strict"):
    _h, digits = handle_error("modhex", errors, decode=True), []
    for i, c in enumerate(ensure_str(text).lower()):
        if c in _DEC:
            digits.append(_DEC[c])
        elif c not in DELIMITERS:
            _h(c, i)
    # an odd number of digits leaves an incomplete byte, which is an error (or dropped if errors are not handled
    #  strictly)
    if len(digits) % 2:
        _h(text[-1:], len(text) - 1)
        digits = digits[:-1]
    return bytes.fromhex("".join(digits)), len(text)


add("modhex", modhex_encode, modhex_decode, r"^(?:mod[-_]?hex|base[-_]?16[-_]modhex|yubikey[-_]modhex)$",
    entropy=4., expansion_factor=2., len_charset=16, printables_rate=1.)
