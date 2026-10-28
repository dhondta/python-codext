# -*- coding: UTF-8 -*-
"""Bech32/Bech32m Codecs - bech32 and bech32m content encodings.

Bech32 (BIP-173) and Bech32m (BIP-350) write the data with a human-readable part (HRP), the separator "1", then the
 data regrouped by 5 bits (the last group being padded with zero bits) in the alphabet
 "qpzry9x8gf2tvdw0s3jn54khce6mua7l", followed by a 6-character BCH checksum computed over the HRP and the data ; both
 only differ by the constant of their checksum.

The HRP is required for encoding (e.g. "bech32-bc") ; without it, a ValueError is raised. When decoding, it is read
 from the text and only checked if given with the codec name ; the data is returned without it. The length limit of 90
 characters of BIP-173 is not enforced.

NB: this does not decode SegWit addresses, whose first data character is the witness version.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki
           https://github.com/bitcoin/bips/blob/master/bip-0350.mediawiki
"""
from ..__common__ import *


_DATA = "\x00\x44\x32\x14\xc7\x42\x54\xb6\x35\xcf\x84\x65\x3a\x56\xd7\xc6\x75\xbe\x77\xdf"
# data whose 5-bit values are 0, 1, ..., 31 (Bech32 test vector) and 31, 30, ..., 0 (Bech32m test vector)
_DATAM = "\xff\xbb\xcd\xeb\x38\xbd\xab\x49\xca\x30\x7b\x9a\xc5\xa9\x28\x39\x8a\x41\x88\x20"
__examples1__ = {
    'enc(bech32)':           {'test': None},
    'enc(bech32-abcdef)':    {_DATA: "abcdef1qpzry9x8gf2tvdw0s3jn54khce6mua7lmqqqxw", '': "abcdef1hu3qdg"},
    'dec(bech32)':           {'abcdef1qpzry9x8gf2tvdw0s3jn54khce6mua7lmqqqxw': _DATA, 'A12UEL5L': "", 'a12uel5l': "",
                              '?1ezyfcl': "", 'split1checkupstagehandshakeupstreamerranterredcaperred2y9e3w':
                              "\xc5\xf3\x8b\x70\x30\x5f\x51\x9b\xf6\x6d\x85\xfb\x6c\xf0\x30\x58\xf3\xdd\xe4\x63\xec\xd7"
                              "\x91\x8f\x2d\xc7\x43\x91\x8f\x2d",
                              "an83characterlonghumanreadablepartthatcontainsthenumber1andtheexcludedcharactersbio"
                              "1tt5tgs": "", 'pzry9x0s0muk': None, '1pzry9x0s0muk': None, 'x1b4n0q5v': None,
                              'li1dgmt3': None, 'A1G7SGD8': None, '10a06t8': None, '1qzzfhee': None,
                              'aBcDef1qpzry9x8gf2tvdw0s3jn54khce6mua7lmqqqxw': None, 'a1lqfn3a': None, 'a1qq': None,
                              "11" + "q" * 82 + "c8247j": "\x00" * 51},
    'dec(bech32-abcdef)':    {'abcdef1qpzry9x8gf2tvdw0s3jn54khce6mua7lmqqqxw': _DATA, 'a12uel5l': None},
    'enc-dec(bech32-a|bech32_bc|bech32-cosmos)': ["", "Hello, World!", "@random{512,1024}"],
}
__examples2__ = {
    'enc(bech32m)':          {'test': None},
    'enc(bech32m-abcdef)':   {_DATAM: "abcdef1l7aum6echk45nj3s0wdvt2fg8x9yrzpqzd3ryx"},
    'dec(bech32m)':          {'abcdef1l7aum6echk45nj3s0wdvt2fg8x9yrzpqzd3ryx': _DATAM, 'a1lqfn3a': "",
                              'A1LQFN3A': "", '?1v759aa': "", 'a12uel5l': None, 'M1VUXWEZ': None, 'abc1rzg': None,
                              # valid Bech32m string, but its padding bits ("11") are not zero, hence no valid bytes
                              "11" + "l" * 82 + "ludsr8": None},
    'enc-dec(bech32m-a|bech32m_bc|bech32m-cosmos)': ["", "Hello, World!", "@random{512,1024}"],
}
__guess1__, __guess2__ = ["bech32"], ["bech32m"]


CHARSET, CONSTANTS = "qpzry9x8gf2tvdw0s3jn54khce6mua7l", {'bech32': 1, 'bech32m': 0x2bc830a3}


def __polymod(values):
    """ BCH checksum computation, as defined in BIP-173. """
    chk = 1
    for v in values:
        b = chk >> 25
        chk = (chk & 0x1ffffff) << 5 ^ v
        for i, g in enumerate((0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3)):
            chk ^= g if b >> i & 1 else 0
    return chk


def __hrp_expand(hrp):
    return [ord(c) >> 5 for c in hrp] + [0] + [ord(c) & 31 for c in hrp]


def __bech32(name, decode=False):
    def _wrapper(hrp=None):
        # an HRP made of digits is given as an integer by the codec name pattern
        hrp = str(hrp or "")
        # a missing HRP is only reported when encoding, as the bare codec name is used for decoding (e.g. when guessing)
        def _code(text, errors="strict"):
            _h, text = handle_error(name, errors, decode=decode, kind="token"), ensure_str(text)
            if not decode:
                if not hrp:
                    raise ValueError(f"Bad parameter for encoding '{name}': a human-readable part is required")
                bits = "".join(f"{x:08b}" for x in b(text))
                bits += "0" * (-len(bits) % 5)
                values = [int(bits[i:i+5], 2) for i in range(0, len(bits), 5)]
                chk = __polymod(__hrp_expand(hrp) + values + [0] * 6) ^ CONSTANTS[name]
                values += [chk >> 5 * (5 - i) & 31 for i in range(6)]
                return (s := hrp + "1" + "".join(CHARSET[v] for v in values)), len(s)
            # strict mode: mixed case, missing separator or HRP, too short checksum, wrong characters or checksum,
            #  wrong HRP and non-zero padding are errors ; otherwise, the data is decoded as far as possible
            if text.lower() != text and text.upper() != text:
                _h(text, 0)
            text = text.lower()
            if (pos := text.rfind("1")) < 1 or pos + 7 > len(text) or any(not 33 <= ord(c) <= 126 for c in text[:pos]):
                return (r := b(_h(text, 0))), len(r)
            h, values = text[:pos], []
            if hrp and h != hrp:
                _h(h, 0)
            for i, c in enumerate(text[pos+1:], pos + 1):
                if c in CHARSET:
                    values.append(CHARSET.index(c))
                else:
                    _h(c, i)
            if __polymod(__hrp_expand(h) + values) != CONSTANTS[name]:
                _h(text[-6:], len(text) - 6)
            bits = "".join(f"{v:05b}" for v in values[:-6])
            if len(bits) % 8 >= 5 or "1" in bits[len(bits) - len(bits) % 8:]:
                _h(text[-7], len(text) - 7)
            r = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits) - 7, 8))
            return r, len(r)
        return _code
    return _wrapper


for _n, _ex, _gs in [("bech32", __examples1__, __guess1__), ("bech32m", __examples2__, __guess2__)]:
    add(_n, __bech32(_n), __bech32(_n, True), rf"^{_n}(?:[-_]([a-z0-9]+))?$", examples=_ex, guess=_gs,
        printables_rate=1., expansion_factor=1.6)
