# -*- coding: UTF-8 -*-
"""Barbie typewriter Codec - barbie content encoding.

While Barbie typewriter is more a cipher, its very limited key size of 2 bits makes it easy to turn into four variants
 of the same encoding.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: http://www.cryptomuseum.com/crypto/mehano/barbie/
"""
from ..__common__ import *


__examples__ = {
    'enc(barbie1)':                   {'\r': None},
    'enc(barbie1|barbie_1|barbie-1)': {'this is a test': "hstf tf i hafh"},
    'enc(barbie2|barbie_2|barbie-2)': {'this is a test': "sfhp hp t sips"},
    'enc(barbie3|barbie_3|barbie-3)': {'this is a test': "fpsu su h ftuf"},
    'enc(barbie4|barbie_4|barbie-4)': {'this is a test': "pufq fq s phqp"},
}
__guess__ = ["barbie-%d" % i for i in range(1, 5)]


STD = [
    "abcdefghijklmnopqrstuvABCDEFGHIJKLMNOPQRSTUVWXYZ0123456 \n\t",
    "icolapxstvybjeruknfhqg>FAUTCYOLVJDZINQKSEHG<.1PB5234067 \n\t",
    "torbiudfhgzcvanqyepskxRC>GHAPND<VUBLIKJETOYXM2QF6340578 \n\t",
    "hrnctqlpsxwogiekzaufydSARYO>QIUX<GFDLJVTHNP1Z3KC7405689 \n\t",
    "sneohkbufd;rxtaywiqpzlE>SPNRKLG1XYCUDV<HOIQ2B4JA805679- \n\t",
]
SPEC = [
    "w x y z 7 8 9 - \' ! \" # % & ( ) * , . ¨ / : ; ? @ ^ _ + < = > ¢ £ § €",
    "; d z w 8 9 - ¨ _ & m @ : \" * ( # W M § ^ , ¢ / ? ! ) % X \' R + € £ =",
    "¢ l w ; 9 - ¨ § ) \" j ? , m # * @ . Z £ ! W + ^ / & ( : 1 _ S % = € \'",
    "+ b ; ¢ - ¨ § £ ( m v / W j @ # ? M B € & . % ! ^ \" * , 2 ) E : \' = _",
    "% c ¢ + ¨ § £ € * j g ^ . v ? @ / Z F = \" N : & ! m # W 3 ( T , _ \' )",
]
ENCMAP = []
for i in range(4):
    encmap = {}
    for j, c in enumerate(STD[0]):
        encmap[c] = STD[i+1][j]
    spec = SPEC[i+1].split()
    for j, c in enumerate(SPEC[0].split()):
        encmap[c] = spec[j]
    ENCMAP.append(encmap)


add_map("barbie", ENCMAP, pattern=r"^barbie[-_]?([1-4])$", printables_rate=lambda pr: .857 * pr)

