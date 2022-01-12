# -*- coding: UTF-8 -*-
"""Case Codecs - string common checksums.

These are codecs for hashing strings, for use with other codecs in encoding chains.

These codecs:
- transform strings from str to str
- transform strings from bytes to bytes
- transform file content from str to bytes (write)
"""
from zlib import adler32

from ..__common__ import add, b


CRC = {
    '': {
        'a':             (0x1021, 0xc6c6, True, True, 0, 0xbf05),
    },
    8: {
        '':              (0x07, 0, False, False, 0, 0xf4),
        'aes':           (0x1d, 0xff, True, True, 0, 0x97),
        'autosar':       (0x2f, 0xff, False, False, 0xff, 0xdf),
        'bluetooth':     (0xa7, 0, True, True, 0, 0x26),
        'cdma2000':      (0x9b, 0xff, False, False, 0, 0xda),
        'dallas-1-wire': (0x31, 0, True, True, 0, 0xa1),
        'darc':          (0x39, 0, True, True, 0, 0x15),
        'dvb-s2':        (0xd5, 0, False, False, 0, 0xbc),
        'ebu':           (0x1d, 0xff, True, True, 0, 0x97),
        'gsm-a':         (0x1d, 0, False, False, 0, 0x37),
        'gsm-b':         (0x49, 0, False, False, 0xff, 0x94),
        'hitag':         (0x1d, 0xff, False, False, 0, 0xb4),
        'i-432-1':       (0x07, 0, False, False, 0x55, 0xa1),
        'i-code':        (0x1d, 0xfd, False, False, 0, 0x7e),
        'itu':           (0x07, 0, False, False, 0x55, 0xa1),
        'lte':           (0x9b, 0, False, False, 0, 0xea),
        'maxim':         (0x31, 0, True, True, 0, 0xa1),
        'maxim-dow':     (0x31, 0, True, True, 0, 0xa1),
        'mifare-mad':    (0x1d, 0xc7, False, False, 0, 0x99),
        'nrsc-5':        (0x31, 0xff, False, False, 0, 0xf7),
        'opensafety':    (0x2f, 0, False, False, 0, 0x3e),
        'rohc':          (0x07, 0xff, True, True, 0, 0xd0),
        'sae-j1850':     (0x1d, 0xff, False, False, 0xff, 0x4b),
        'smbus':         (0x07, 0, False, False, 0, 0xf4),
        'tech-3250':     (0x1d, 0xff, True, True, 0, 0x97),
        'wcdma':         (0x9b, 0, True, True, 0, 0x25),
    },
    10: {
        '':              (0x233, 0, False, False, 0, 0x199),
        'atm':           (0x233, 0, False, False, 0, 0x199),
        'cdma2000':      (0x3d9, 0x3ff, False, False, 0, 0x233),
        'gsm':           (0x175, 0, False, False, 0x3ff, 0x12a),
        'i-610':         (0x233, 0, False, False, 0, 0x199),
    },
    11: {
        '':              (0x385, 0x01a, False, False, 0, 0x5a3),
        'flexray':       (0x385, 0x01a, False, False, 0, 0x5a3),
        'umts':          (0x307, 0, False, False, 0, 0x061),
    },
    12: {
        '':              (0x80f, 0, False, True, 0, 0xdaf),
        '3gpp':          (0x80f, 0, False, True, 0, 0xdaf),
        'cdma2000':      (0xf13, 0xfff, False, False, 0, 0xd4d),
        'dect':          (0x80f, 0, False, False, 0, 0xf5b),
        'gsm':           (0xd31, 0, False, False, 0xfff, 0xb34),
        'umts':          (0x80f, 0, False, True, 0, 0xdaf),
    },
    13: {
        '':              (0x1cf5, 0, False, False, 0, 0x04fa),
        'bbc':           (0x1cf5, 0, False, False, 0, 0x04fa),
    },
    14: {
        '':              (0x0805, 0, True, True, 0, 0x082d),
        'darc':          (0x0805, 0, True, True, 0, 0x082d),
        'gsm':           (0x202d, 0, False, False, 0x3fff, 0x30ae),
    },
    15: {
        '':              (0x4599, 0, False, False, 0, 0x059e),
        'can':           (0x4599, 0, False, False, 0, 0x059e),
        'mpt1327':       (0x6815, 0, False, False, 1, 0x2566),
    },
    16: {
        'acorn':         (0x1021, 0, False, False, 0, 0x31c3),
        'arc':           (0x8005, 0, True, True, 0, 0xbb3d),
        'atom':          (0x002d, 0, True, True, 0, 0x4287),
        'aug-2-ccitt':   (0x1021, 0x84c0, False, False, 0, 0x19cf),
        'aug-2-citt':    (0x1021, 0x84c0, False, False, 0, 0x19cf),
        'aug-ccitt':     (0x1021, 0x1d0f, False, False, 0, 0xe5cc),
        'aug-citt':      (0x1021, 0x1d0f, False, False, 0, 0xe5cc),
        'autosar':       (0x1021, 0xffff, False, False, 0, 0x29b1),
        'bt-chip':       (0x1021, 0xffff, True, False, 0, 0x89f6),
        'buypass':       (0x8005, 0, False, False, 0, 0xfee8),
        'cms':           (0x8005, 0xffff, False, False, 0, 0xaee7),
        'ccitt':         (0x1021, 0, True, True, 0, 0x2189),
        'ccitt-false':   (0x1021, 0xffff, False, False, 0, 0x29b1),
        'ccitt-true':    (0x1021, 0, True, True, 0, 0x2189),
        'cdma2000':      (0xc867, 0xffff, False, False, 0, 0x4c06),
        'darc':          (0x1021, 0xffff, False, False, 0xffff, 0xd64e),
        'dds-110':       (0x8005, 0x800d, False, False, 0, 0x9ecf),
        'dect-r':        (0x0589, 0, False, False, 1, 0x007e),
        'dect-x':        (0x0589, 0, False, False, 0, 0x007f),
        'dnp':           (0x3d65, 0, True, True, 0xffff, 0xea82),
        'en-13757':      (0x3d65, 0, False, False, 0xffff, 0xc2b7),
        'epc':           (0x1021, 0xffff, False, False, 0xffff, 0xd64e),
        'epc-c1g2':      (0x1021, 0xffff, False, False, 0xffff, 0xd64e),
        'genibus':       (0x1021, 0xffff, False, False, 0xffff, 0xd64e),
        'gsm':           (0x1021, 0, False, False, 0xffff, 0xce3c),
        'i-code':        (0x1021, 0xffff, False, False, 0xffff, 0xd64e),
        'ibm':           (0x8005, 0, True, True, 0, 0xbb3d),
        'ibm-3740':      (0x1021, 0xffff, False, False, 0, 0x29b1),
        'ibm-sdlc':      (0x1021, 0xffff, True, True, 0xffff, 0x906e),
        'iec-61158-2':   (0x1dcf, 0xffff, False, False, 0xffff, 0xa819),
        'iso-hdlc':      (0x1021, 0xffff, True, True, 0xffff, 0x906e),
        'kermit':        (0x1021, 0, True, True, 0, 0x2189),
        'lha':           (0x8005, 0, True, True, 0, 0xbb3d),
        'lj1200':        (0x6f63, 0, False, False, 0, 0xbdf4),
        'maxim':         (0x8005, 0, True, True, 0xffff, 0x44c2),
        'maxim-dom':     (0x8005, 0, True, True, 0xffff, 0x44c2),
        'mcrf4xx':       (0x1021, 0xffff, True, True, 0, 0x6f91),
        'modbus':        (0x8005, 0xffff, True, True, 0, 0x4b37),
        'opensafety-a':  (0x5935, 0, False, False, 0, 0x5d38),
        'opensafety-b':  (0x755b, 0, False, False, 0, 0x20fe),
        'profibus':      (0x1dcf, 0xffff, False, False, 0xffff, 0xa819),
        'riello':        (0x1021, 0xb2aa, True, True, 0, 0x63d0),
        'spi-fujitsu':   (0x1021, 0x84c0, False, False, 0, 0x19cf),
        't10-dif':       (0x8bb7, 0, False, False, 0, 0xd0db),
        'teledisk':      (0xa097, 0, False, False, 0, 0x0fb3),
        'tms37157':      (0x1021, 0x89ec, True, True, 0, 0x26b1),
        'umts':          (0x8005, 0, False, False, 0, 0xfee8),
        'usb':           (0x8005, 0xffff, True, True, 0xffff, 0xb4c8),
        'v-41-lsb':      (0x1021, 0, True, True, 0, 0x2189),
        'verifone':      (0x8005, 0, False, False, 0, 0xfee8),
        'x-25':          (0x1021, 0xffff, True, True, 0xffff, 0x906e),
        'x-kermit':      (0x8408, 0, True, True, 0, 0x0c73),
        'x-xmodem':      (0x8408, 0, True, True, 0, 0x0c73),
        'xmodem':        (0x1021, 0, False, False, 0, 0x31c3),
        'zmodem':        (0x1021, 0, False, False, 0, 0x31c3),
    },
    17: {
        '':              (0x1685b, 0, False, False, 0, 0x04f03),
        'can-fd':        (0x1685b, 0, False, False, 0, 0x04f03),
    },
    21: {
        '':              (0x102899, 0, False, False, 0, 0x0ed841),
        'can-fd':        (0x102899, 0, False, False, 0, 0x0ed841),
    },
    24: {
        '':              (0x864cfb, 0xb704ce, False, False, 0, 0x21cf02),
        'ble':           (0x00065b, 0x555555, True, True, 0, 0xc25a56),
        'flexray-a':     (0x5d6dcb, 0xfedcba, False, False, 0, 0x7979bd),
        'flexray-b':     (0x5d6dcb, 0xabcdef, False, False, 0, 0x1f23b8),
        'interlaken':    (0x328b63, 0xffffff, False, False, 0xffffff, 0xb4f3e6),
        'lte-a':         (0x864cfb, 0, False, False, 0, 0xcde703),
        'lte-b':         (0x800063, 0, False, False, 0, 0x23ef52),
        'openpgp':       (0x864cfb, 0xb704ce, False, False, 0, 0x21cf02),
        'os-9':          (0x800063, 0xffffff, False, False, 0xffffff, 0x200fa5),
        'pgp':           (0x864cfb, 0xb704ce, False, False, 0, 0x21cf02),
    },
    30: {
        '':              (0x2030b9c7, 0x3fffffff, False, False, 0x3fffffff, 0x04c34abf),
        'cdma':          (0x2030b9c7, 0x3fffffff, False, False, 0x3fffffff, 0x04c34abf),
    },
    31: {
        '':              (0x04c11db7, 0x7fffffff, False, False, 0x7fffffff, 0x0ce9e46c),
        'philips':       (0x04c11db7, 0x7fffffff, False, False, 0x7fffffff, 0x0ce9e46c),
    },
    32: {
        '':              (0x04c11db7, 0xffffffff, True, True, 0xffffffff, 0xcbf43926),
        'aal5':          (0x04c11db7, 0xffffffff, False, False, 0xffffffff, 0xfc891918),
        'adccp':         (0x04C11db7, 0xffffffff, True, True, 0xffffffff, 0xcbf43926),
        'aixm':          (0x814141ab, 0, False, False, 0, 0x3010bf7f),
        'autosar':       (0xf4acfb13, 0xffffffff, True, True, 0xffffffff, 0x1697d06a),
        'b':             (0x04c11db7, 0xffffffff, False, False, 0xffffffff, 0xfc891918),
        'base91-c':      (0x1edc6f41, 0xffffffff, True, True, 0xffffffff, 0xe3069283),
        'base91-d':      (0xa833982b, 0xffffffff, True, True, 0xffffffff, 0x87315576),
        'bzip2':         (0x04c11db7, 0xffffffff, False, False, 0xffffffff, 0xfc891918),
        'c':             (0x1edc6f41, 0xffffffff, True, True, 0xffffffff, 0xe3069283),
        'castagnoli':    (0x1edc6f41, 0xffffffff, True, True, 0xffffffff, 0xe3069283),
        'cd-rom-edc':    (0x8001801b, 0, True, True, 0, 0x6ec2edc4),
        'cksum':         (0x04c11db7, 0, False, False, 0xffffffff, 0x765e7680),
        'd':             (0xa833982b, 0xffffffff, True, True, 0xffffffff, 0x87315576),
        'dect-b':        (0x04c11db7, 0xffffffff, False, False, 0xffffffff, 0xfc891918),
        'interlaken':    (0x1edc6f41, 0xffffffff, True, True, 0xffffffff, 0xe3069283),
        'iscsi':         (0x1edc6f41, 0xffffffff, True, True, 0xffffffff, 0xe3069283),
        'iso-hdlc':      (0x04c11db7, 0xffffffff, True, True, 0xffffffff, 0xcbf43926),
        'jamcrc':        (0x04c11db7, 0xffffffff, True, True, 0, 0x340bc6d9),
        'mpeg-2':        (0x04c11db7, 0xffffffff, False, False, 0, 0x0376e6e7),
        'mpeg2':         (0x04c11db7, 0xffffffff, False, False, 0, 0x0376e6e7),
        'posix':         (0x04c11db7, 0, False, False, 0xffffffff, 0x765e7680),
        'q':             (0x814141ab, 0, False, False, 0, 0x3010bf7f),
        'v-42':          (0x04C11db7, 0xffffffff, True, True, 0xffffffff, 0xcbf43926),
        'xfer':          (0x000000af, 0, False, False, 0, 0xbd0be338),
        'xz':            (0x04C11db7, 0xffffffff, True, True, 0xffffffff, 0xcbf43926),
        'zip':           (0x04C11DB7, 0xffffffff, True, True, 0xffffffff, 0xcbf43926),
    },
    40: {
        '':              (0x0004820009, 0, False, False, 0xffffffffff, 0xd4164fc646),
        'gsm':           (0x0004820009, 0, False, False, 0xffffffffff, 0xd4164fc646),
    },
    64: {
        '':              (0x000000000000001b, 0xffffffffffffffff, True, True, 0xffffffffffffffff, 0xb90956c775a41001),
        'ecma':          (0x42f0e1eba9ea3693, 0, False, False, 0, 0x6c40df5f0b497347),
        'ecma-182':      (0x42f0e1eba9ea3693, 0, False, False, 0, 0x6c40df5f0b497347),
        'go-ecma':       (0x42f0e1eba9ea3693, 0xffffffffffffffff, True, True, 0xffffffffffffffff, 0x995dc9bbdf1939fa),
        'go-iso':        (0x000000000000001b, 0xffffffffffffffff, True, True, 0xffffffffffffffff, 0xb90956c775a41001),
        'iso':           (0x000000000000001b, 0xffffffffffffffff, True, True, 0xffffffffffffffff, 0xb90956c775a41001),
        'we':            (0x42f0e1eba9ea3693, 0xffffffffffffffff, False, False, 0xffffffffffffffff, 0x62ec59e3f1a4f00a),
        'xz':            (0x42f0e1eba9ea3693, 0xffffffffffffffff, True, True, 0xffffffffffffffff, 0x995dc9bbdf1939fa),
        'xz64':          (0x42f0e1eba9ea3693, 0xffffffffffffffff, True, True, 0xffffffffffffffff, 0x995dc9bbdf1939fa),
    },
    82: {
        '':              (0x0308c0111011401440411, 0, True, True, 0, 0x09ea83f625023801fd612),
        'darc':          (0x0308c0111011401440411, 0, True, True, 0, 0x09ea83f625023801fd612),
    },
}

_pattern = lambda n="": r"^crc" + str(n) + r"(|[-_]?(?:%s))$" % "|".join(x for x in CRC[n].keys() if len(x) > 0)
_rev_int = lambda i, l=None: int(bin(i)[2:].zfill(l or len(bin(i)[2:]))[::-1], 2)


def crc(data, length, poly, init=0, refl_in=False, refl_out=False, xor_out=0):
    """ Generic CRC computation function. """
    table = [None] * 256
    # input reflected
    if refl_in:
        init, poly = _rev_int(init, length), _rev_int(poly, length)
        # prepare the lookup table
        for x in range(2**8):
            crc = x
            for i in range(8):
                crc = (crc >> 1) ^ [0, poly][crc & 0x1 != 0]
            table[x] = crc
        # compute CRC
        crc = init
        for c in data:
            crc = (crc >> 8) ^ table[(crc ^ ord(c)) & 0xff]
    # input NOT reflected
    else:
        # prepare the lookup table
        for x in range(2**8):
            crc = x << (length - 8)
            for i in range(8):
                crc = ((crc << 1) & ((1 << length) - 1)) ^ [0, poly][crc >> (length - 1) != 0]
            table[x] = crc
        # compute CRC
        crc = init
        for c in data:
            crc = ((crc << 8) & ((1 << length) - 1)) ^ table[(crc >> (length - 8)) ^ ord(c)]
    # output reflected
    if refl_in ^ refl_out:
        crc = _rev_int(crc, length)
    return crc ^ xor_out


def crc_checksum(n=""):
    def _crc(name):
        def _encode(data, error="strict"):
            r = crc(data, n or 16, *CRC[n][name.lstrip("-_")][:5])
            return "%0{}x".format(round((n or 16)/4+.5)) % r, len(data)
        return _encode
    return _crc


add("adler32", lambda data, error="strict": (adler32(b(data)) & 0xffffffff, len(data)), guess=None)
add("crca", crc_checksum(), pattern=_pattern(), guess=None)
for i in CRC.keys():
    if isinstance(i, int):
        add("crc%d" % i, crc_checksum(i), pattern=_pattern(i), guess=None)

