# -*- coding: UTF-8 -*-
"""GOST Hashing Codec - string hashing with GOST R 34.11-2012 (Streebog).

Streebog, defined in the Russian standard GOST R 34.11-2012 (RFC 6986), is a hash function with 256-bit and 512-bit
 digests. Its compression function is a 12-round block cipher on 512-bit states, each round being a byte substitution,
 a byte transposition and a linear transformation (a multiplication by a matrix over GF(2)), the message being processed
 by blocks of 64 bytes and the result being completed with the length of the message and the sum of its blocks. This
 codec returns the hexadecimal digest (one-way), for use with other codecs in encoding chains, in the byte order of the
 usual implementations (e.g. CyberChef's), i.e. the reverse of the order of the examples of RFC 6986. The digest size
 is given in the codec name ("gosthash-256" or "gosthash-512") and defaults to 256 bits.

This codec:
- transforms strings from str to str
- transforms strings from bytes to bytes
- transforms file content from str to bytes (write)

Reference: https://datatracker.ietf.org/doc/html/rfc6986
"""
from struct import pack, unpack

from ..__common__ import *


# nonlinear bijection, rows of the matrix of the linear transformation, and iteration constants (see RFC 6986 ; the
#  first iteration constant is printed with a repeated line in the RFC)
PI = [
    252, 238, 221, 17, 207, 110, 49, 22, 251, 196, 250, 218, 35, 197, 4, 77, 233, 119, 240, 219, 147, 46, 153, 186, 23,
    54, 241, 187, 20, 205, 95, 193, 249, 24, 101, 90, 226, 92, 239, 33, 129, 28, 60, 66, 139, 1, 142, 79, 5, 132, 2,
    174, 227, 106, 143, 160, 6, 11, 237, 152, 127, 212, 211, 31, 235, 52, 44, 81, 234, 200, 72, 171, 242, 42, 104, 162,
    253, 58, 206, 204, 181, 112, 14, 86, 8, 12, 118, 18, 191, 114, 19, 71, 156, 183, 93, 135, 21, 161, 150, 41, 16,
    123, 154, 199, 243, 145, 120, 111, 157, 158, 178, 177, 50, 117, 25, 61, 255, 53, 138, 126, 109, 84, 198, 128, 195,
    189, 13, 87, 223, 245, 36, 169, 62, 168, 67, 201, 215, 121, 214, 246, 124, 34, 185, 3, 224, 15, 236, 222, 122, 148,
    176, 188, 220, 232, 40, 80, 78, 51, 10, 74, 167, 151, 96, 115, 30, 0, 98, 68, 26, 184, 56, 130, 100, 159, 38, 65,
    173, 69, 70, 146, 39, 94, 85, 47, 140, 163, 165, 125, 105, 213, 149, 59, 7, 88, 179, 64, 134, 172, 29, 247, 48, 55,
    107, 228, 136, 217, 231, 137, 225, 27, 131, 73, 76, 63, 248, 254, 141, 83, 170, 144, 202, 216, 133, 97, 32, 113,
    103, 164, 45, 43, 9, 91, 203, 155, 37, 208, 190, 229, 108, 82, 89, 166, 116, 210, 230, 244, 180, 192, 209, 102,
    175, 194, 57, 75, 99, 182,
]
A = [
    0x8e20faa72ba0b470, 0x47107ddd9b505a38, 0xad08b0e0c3282d1c, 0xd8045870ef14980e, 0x6c022c38f90a4c07,
    0x3601161cf205268d, 0x1b8e0b0e798c13c8, 0x83478b07b2468764, 0xa011d380818e8f40, 0x5086e740ce47c920,
    0x2843fd2067adea10, 0x14aff010bdd87508, 0x0ad97808d06cb404, 0x05e23c0468365a02, 0x8c711e02341b2d01,
    0x46b60f011a83988e, 0x90dab52a387ae76f, 0x486dd4151c3dfdb9, 0x24b86a840e90f0d2, 0x125c354207487869,
    0x092e94218d243cba, 0x8a174a9ec8121e5d, 0x4585254f64090fa0, 0xaccc9ca9328a8950, 0x9d4df05d5f661451,
    0xc0a878a0a1330aa6, 0x60543c50de970553, 0x302a1e286fc58ca7, 0x18150f14b9ec46dd, 0x0c84890ad27623e0,
    0x0642ca05693b9f70, 0x0321658cba93c138, 0x86275df09ce8aaa8, 0x439da0784e745554, 0xafc0503c273aa42a,
    0xd960281e9d1d5215, 0xe230140fc0802984, 0x71180a8960409a42, 0xb60c05ca30204d21, 0x5b068c651810a89e,
    0x456c34887a3805b9, 0xac361a443d1c8cd2, 0x561b0d22900e4669, 0x2b838811480723ba, 0x9bcf4486248d9f5d,
    0xc3e9224312c8c1a0, 0xeffa11af0964ee50, 0xf97d86d98a327728, 0xe4fa2054a80b329c, 0x727d102a548b194e,
    0x39b008152acb8227, 0x9258048415eb419d, 0x492c024284fbaec0, 0xaa16012142f35760, 0x550b8e9e21f7a530,
    0xa48b474f9ef5dc18, 0x70a6a56e2440598e, 0x3853dc371220a247, 0x1ca76e95091051ad, 0x0edd37c48a08a6d8,
    0x07e095624504536c, 0x8d70c431ac02a736, 0xc83862965601dd1b, 0x641c314b2b8ee083,
]
C = [
    "b1085bda1ecadae9ebcb2f81c0657c1f2f6a76432e45d016714eb88d7585c4fc"
    "4b7ce09192676901a2422a08a460d31505767436cc744d23dd806559f2a64507",
    "6fa3b58aa99d2f1a4fe39d460f70b5d7f3feea720a232b9861d55e0f16b50131"
    "9ab5176b12d699585cb561c2db0aa7ca55dda21bd7cbcd56e679047021b19bb7",
    "f574dcac2bce2fc70a39fc286a3d843506f15e5f529c1f8bf2ea7514b1297b7b"
    "d3e20fe490359eb1c1c93a376062db09c2b6f443867adb31991e96f50aba0ab2",
    "ef1fdfb3e81566d2f948e1a05d71e4dd488e857e335c3c7d9d721cad685e353f"
    "a9d72c82ed03d675d8b71333935203be3453eaa193e837f1220cbebc84e3d12e",
    "4bea6bacad4747999a3f410c6ca923637f151c1f1686104a359e35d7800fffbd"
    "bfcd1747253af5a3dfff00b723271a167a56a27ea9ea63f5601758fd7c6cfe57",
    "ae4faeae1d3ad3d96fa4c33b7a3039c02d66c4f95142a46c187f9ab49af08ec6"
    "cffaa6b71c9ab7b40af21f66c2bec6b6bf71c57236904f35fa68407a46647d6e",
    "f4c70e16eeaac5ec51ac86febf240954399ec6c7e6bf87c9d3473e33197a93c9"
    "0992abc52d822c3706476983284a05043517454ca23c4af38886564d3a14d493",
    "9b1f5b424d93c9a703e7aa020c6e41414eb7f8719c36de1e89b4443b4ddbc49a"
    "f4892bcb929b069069d18d2bd1a5c42f36acc2355951a8d9a47f0dd4bf02e71e",
    "378f5a541631229b944c9ad8ec165fde3a7d3a1b258942243cd955b7e00d0984"
    "800a440bdbb2ceb17b2b8a9aa6079c540e38dc92cb1f2a607261445183235adb",
    "abbedea680056f52382ae548b2e4f3f38941e71cff8a78db1fffe18a1b336103"
    "9fe76702af69334b7a1e6c303b7652f43698fad1153bb6c374b4c7fb98459ced",
    "7bcd9ed0efc889fb3002c6cd635afe94d8fa6bbbebab07612001802114846679"
    "8a1d71efea48b9caefbacd1d7d476e98dea2594ac06fd85d6bcaa4cd81f32d1b",
    "378ee767f11631bad21380b00449b17acda43c32bcdf1d77f82012d430219f9b"
    "5d80ef9d1891cc86e71da4aa88e12852faf417d5d9b21b9948bc924af11bd720",
]

_M = (1 << 512) - 1
# combined substitution, transposition and linear transformation: _T[j][b] is the contribution of the byte b of the
#  64-bit word j of the state to each output word
_T = [[0] * 256 for _ in range(8)]
for _j in range(8):
    for _b in range(256):
        _v, _x = 0, PI[_b]
        for _k in range(8):
            if _x >> _k & 1:
                _v ^= A[63 - 8 * _j - _k]
        _T[_j][_b] = _v
_C = [unpack("<8Q", bytes.fromhex(c)[::-1]) for c in C]


def _lps(w):
    return [_T[0][w[0] >> s & 255] ^ _T[1][w[1] >> s & 255] ^ _T[2][w[2] >> s & 255] ^ _T[3][w[3] >> s & 255] ^
            _T[4][w[4] >> s & 255] ^ _T[5][w[5] >> s & 255] ^ _T[6][w[6] >> s & 255] ^ _T[7][w[7] >> s & 255]
            for s in range(0, 64, 8)]


def _g(n, h, m):
    """ Compression function g_N(h, m), on states given as 8 little-endian 64-bit words. """
    k = _lps([a ^ b for a, b in zip(h, _words(n))])
    t = m
    for c in _C:
        t = _lps([a ^ b for a, b in zip(k, t)])
        k = _lps([a ^ b for a, b in zip(k, c)])
    return [a ^ b ^ c ^ d for a, b, c, d in zip(k, t, h, m)]


def _words(n):
    return unpack("<8Q", n.to_bytes(64, "little"))


def streebog(data, size=256):
    """ Streebog digest of the data, with the given size in bits. """
    h, n, sigma = [0x0101010101010101 if size == 256 else 0] * 8, 0, 0
    for i in range(0, len(data) - 63, 64):
        m = unpack("<8Q", data[i:i+64])
        h = _g(n, h, m)
        n, sigma = (n + 512) & _M, (sigma + int.from_bytes(data[i:i+64], "little")) & _M
    rest = data[len(data) - len(data) % 64:]
    block = (rest + b"\x01").ljust(64, b"\x00")
    h = _g(n, h, unpack("<8Q", block))
    n, sigma = (n + 8 * len(rest)) & _M, (sigma + int.from_bytes(block, "little")) & _M
    h = _g(0, _g(0, h, list(_words(n))), list(_words(sigma)))
    return pack("<8Q", *h)[64 - size // 8:]


def gosthash(size):
    size = int(size or 256)
    def _hash(text, errors="strict"):
        return streebog(b(text), size).hex(), len(text)
    return _hash


add("gosthash", gosthash, pattern=r"^(?:gost[-_]?hash|streebog)(?:[-_]?(256|512))?$", guess=None)
