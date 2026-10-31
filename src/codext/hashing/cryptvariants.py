# -*- coding: UTF-8 -*-
"""Crypt Variants Hashing Codecs - string hashing with the traditional crypt(3) password hash variants.

These codecs implement the password hash variants of crypt(3) that are not provided by the crypt module (hence
 available on every platform): "bigcrypt" (DES crypt extended to long passwords, 11 characters of hash per 8-character
 block), "crypt16" (two DES computations, of 20 and 5 rounds), "bsdi-crypt" (the extended DES scheme of BSDi, with a
 24-bit salt and a configurable number of rounds given with the codec name, e.g. "bsdi-crypt-5001"), "bsd-nthash" (the
 NT hash in the "$3$$" modular crypt format of modern BSD) and "sun-md5-crypt" (the MD5-based scheme of Solaris, the
 number of rounds, added to 4096, being given with the codec name, e.g. "sun-md5-crypt-5000"). A random salt is
 generated each time (except for bsd-nthash, which has none), hence the output differs between calls. These codecs
 return the hash string (one-way), for use with other codecs in encoding chains.

These codecs:
- transform strings from str to str
- transform strings from bytes to bytes
- transform file content from str to bytes (write)

Reference: https://passlib.readthedocs.io/en/stable/modular_crypt_format.html
"""
import os

from ._descrypt import des_int, secret_to_key
from ._h64 import ALPHABET, encode_bytes, encode_transposed, encode_int64, encode_int24, decode_int12, decode_int24
from .md import md4
from ..__common__ import *


def _salt(n):
    return "".join(ALPHABET[c & 63] for c in os.urandom(n))


# constants of the Sun MD5 crypt hash: Hamlet's soliloquy (used as a conditional extra input), the bit-selection rounds
#  and the order in which the digest bytes are encoded (see the reference implementation)
MAGIC_HAMLET = (
    b"To be, or not to be,--that is the question:--\nWhether 'tis nobler in the mind to suffer\nThe slings and arr"
    b"ows of outrageous fortune\nOr to take arms against a sea of troubles,\nAnd by opposing end them?--To die,--t"
    b"o sleep,--\nNo more; and by a sleep to say we end\nThe heartache, and the thousand natural shocks\nThat fles"
    b"h is heir to,--'tis a consummation\nDevoutly to be wish'd. To die,--to sleep;--\nTo sleep! perchance to drea"
    b"m:--ay, there's the rub;\nFor in that sleep of death what dreams may come,\nWhen we have shuffled off this m"
    b"ortal coil,\nMust give us pause: there's the respect\nThat makes calamity of so long life;\nFor who would be"
    b"ar the whips and scorns of time,\nThe oppressor's wrong, the proud man's contumely,\nThe pangs of despis'd l"
    b"ove, the law's delay,\nThe insolence of office, and the spurns\nThat patient merit of the unworthy takes,\nW"
    b"hen he himself might his quietus make\nWith a bare bodkin? who would these fardels bear,\nTo grunt and sweat"
    b" under a weary life,\nBut that the dread of something after death,--\nThe undiscover'd country, from whose b"
    b"ourn\nNo traveller returns,--puzzles the will,\nAnd makes us rather bear those ills we have\nThan fly to oth"
    b"ers that we know not of?\nThus conscience does make cowards of us all;\nAnd thus the native hue of resolutio"
    b"n\nIs sicklied o'er with the pale cast of thought;\nAnd enterprises of great pith and moment,\nWith this reg"
    b"ard, their currents turn awry,\nAnd lose the name of action.--Soft you now!\nThe fair Ophelia!--Nymph, in th"
    b"y orisons\nBe all my sins remember'd.\n\x00"
)

_XY_ROUNDS = (
    ((0, 0, 3), (1, 1, 4), (2, 2, 5), (3, 3, 6), (4, 4, 7), (5, 5, 8), (6, 6, 9)),
    ((0, 1, 4), (1, 2, 5), (2, 3, 6), (3, 4, 7), (4, 5, 8), (5, 6, 9), (6, 7, 10)),
    ((0, 8, 11), (1, 9, 12), (2, 10, 13), (3, 11, 14), (4, 12, 15), (5, 13, 0), (6, 14, 1)),
    ((0, 9, 12), (1, 10, 13), (2, 11, 14), (3, 12, 15), (4, 13, 0), (5, 14, 1), (6, 15, 2)),
)

_CHK_OFFSETS = (12, 6, 0, 13, 7, 1, 14, 8, 2, 15, 9, 3, 5, 10, 4, 11)


def _raw_sun_md5(secret, rounds, config):
    """ Compute the Sun MD5 crypt digest of the secret, salted with the config string, over 4096 + rounds rounds. """
    result = hashlib.md5(secret + config).digest()
    xr0, xr1, yr0, yr1 = _XY_ROUNDS
    for rnd in range(4096 + max(rounds, 0)):
        rval = result.__getitem__
        x = 0
        for i, ia, ib in (xr1 if (rval((rnd >> 3) & 15) >> (rnd & 7)) & 1 else xr0):
            a, b = rval(ia), rval(ib)
            v = rval((a >> (b % 5)) & 15) >> ((b >> (a & 7)) & 1)
            x |= ((rval((v >> 3) & 15) >> (v & 7)) & 1) << i
        y = 0
        for i, ia, ib in (yr1 if (rval(((rnd + 64) >> 3) & 15) >> (rnd & 7)) & 1 else yr0):
            a, b = rval(ia), rval(ib)
            v = rval((a >> (b % 5)) & 15) >> ((b >> (a & 7)) & 1)
            y |= ((rval((v >> 3) & 15) >> (v & 7)) & 1) << i
        coin = ((rval(x >> 3) >> (x & 7)) ^ (rval(y >> 3) >> (y & 7))) & 1
        h = hashlib.md5(result)
        if coin:
            h.update(MAGIC_HAMLET)
        h.update(str(rnd).encode("ascii"))
        result = h.digest()
    return encode_transposed(result, _CHK_OFFSETS)


def bigcrypt(text, errors="strict"):
    data, salt = b(ensure_str(text)), _salt(2)
    chk = encode_int64(des_int(secret_to_key(data), decode_int12(salt), 25))
    i = 8
    while i < len(data):
        chk += encode_int64(des_int(secret_to_key(data[i:i+8]), decode_int12(chk[-11:-9]), 25))
        i += 8
    return salt + chk, len(text)


def crypt16(text, errors="strict"):
    data, salt = b(ensure_str(text)), _salt(2)
    s = decode_int12(salt)
    return salt + encode_int64(des_int(secret_to_key(data[:8]), s, 20)) + \
        encode_int64(des_int(secret_to_key(data[8:16]), s, 5)), len(text)


def bsdi_crypt(rounds=None):
    rounds = int(rounds) if rounds not in (None, "") else 5001
    if not 1 <= rounds <= 0xffffff:
        raise LookupError("Bad parameter for encoding 'bsdi-crypt': rounds must be between 1 and 16777215")
    def _hash(text, errors="strict"):
        data, salt = b(ensure_str(text)), _salt(4)
        # the DES key folds the password by blocks of 8 bytes (encrypting the running key and XORing the next block)
        key, i = secret_to_key(data[:8]), 8
        while i < len(data):
            key = des_int(key, 0, 1, key) ^ secret_to_key(data[i:i+8])
            i += 8
        return "_" + encode_int24(rounds) + salt + encode_int64(des_int(key, decode_int24(salt), rounds)), len(text)
    return _hash


def bsd_nthash(text, errors="strict"):
    return "$3$$" + md4(ensure_str(text).encode("utf-16-le")), len(text)


def sun_md5_crypt(rounds=None):
    rounds = int(rounds) if rounds not in (None, "") else 34000
    def _hash(text, errors="strict"):
        salt = _salt(8)
        config = ("$md5,rounds=%d$" % rounds if rounds > 0 else "$md5$") + salt + "$"
        return config + "$" + _raw_sun_md5(b(ensure_str(text)), rounds, config.encode("ascii")), len(text)
    return _hash


add("bigcrypt", bigcrypt, pattern=r"^bigcrypt$", guess=None)
add("crypt16", crypt16, pattern=r"^crypt[-_]?16$", guess=None)
add("bsdi-crypt", bsdi_crypt, pattern=r"^bsdi[-_]?crypt(?:[-_](\d+))?$", guess=None)
add("bsd-nthash", bsd_nthash, pattern=r"^bsd[-_]?nt(?:hash)?$", guess=None)
add("sun-md5-crypt", sun_md5_crypt, pattern=r"^sun[-_]?md5(?:[-_]crypt)?(?:[-_](\d+))?$", guess=None)
