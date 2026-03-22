# -*- coding: UTF-8 -*-
"""BaseN Codecs - base content encodings.

These codecs:
- en/decode strings from str to str
- en/decode strings from bytes to bytes
- decode file content to str (read)
- encode file content from str to bytes (write)
"""
from ..__common__ import *
from ._base import base, base_generic, digits, lower, main, upper
from ._base2n import base2n


B1 = {chr(i): chr(i) for i in range(2**8)}
B1[''] = "A"
base(B1, r"^(?:base[-_]?1(|[-_].)|unary)$", guess=[])
main1 = main(1)


B2 = {r'': "01", r'[-_]inv(erted)?$': "10"}
base2n(B2, r"^(?:base[-_]?2|bin(?:ary)?)(|[-_]inv(?:erted)?|[-_](?!.*(.).*\2)[a-zA-Z0-9]{2})$", expansion_factor=8.)
main2 = main(2)


B3 = {r'': "123", r'[-_]inv(erted)?$': "321"}
base(B3, r"^base[-_]?3(|[-_]inv(?:erted)?|[-_](?!.*(.).*\2)[a-zA-Z0-9]{3})$", expansion_factor=5.)
main3 = main(3)


B4 = {r'': "1234", r'[-_]inv(erted)?$': "4321"}
base2n(B4, r"^base[-_]?4(|[-_]inv(?:erted)?|[-_](?!.*(.).*\2)[a-zA-Z0-9]{4})$", expansion_factor=4.)
main4 = main(4)


B8 = {r'': "abcdefgh", r'[-_]inv(erted)?$': "hgfedcba"}
base2n(B8, r"^base[-_]?8(|[-_]inv(?:erted)?|[-_](?!.*(.).*\2)[a-zA-Z0-9]{8})$")
main8 = main(8)


B10 = {r'': "0123456789"}
base(B10, r"^(?:base[-_]?10|int(?:eger)?|dec(?:imal)?)$")
main10 = main(10)


B11 = {r'': "0123456789a", r'[-_]inv(erted)?$': "a0123456789"}
base(B11, r"^base[-_]?11(|[-_]inv(?:erted)?)$")
main11 = main(11)


B16 = {'': digits + "ABCDEF", '[-_]inv(erted)?$': "ABCDEF" + digits}
base2n(B16, r"^(?:base[-_]?16|hex)(|[-_]inv(?:erted)?)$", expansion_factor=2.)
main16 = main(16, "RFC 4648")


B26 = {'': upper}
base(B26, r"^base[-_]?26$")
main26 = main(26, inv=False)


B32 = {
    r'':                                upper + "234567",
    r'[-_]?z(?:base32)?$':              "ybndrfg8ejkmcpqxot1uwisza345h769",
    r'[-_]inv(erted)?$':                "234567" + upper,
    r'(?:[-_](ext(ended)?)?)?[-_]hex$': digits + upper[:22],
    r'[-_]?crockford':                  digits + "ABCDEFGHJKMNPQRSTVWXYZ",
    r'[-_]?geohash':                    digits + "bcdefghjkmnpqrstuvwxyz",
}
base2n(B32, r"^(?:base[-_]?32(|[-_]inv(?:erted)?|(?:[-_]ext(?:ended)?)?[-_]hex|[-_](?:z|geohash|crockford))|"
       r"(zbase32|geohash|crockford))$", padding_char="=",
       guess=["base32", "base32-inv", "base32-hex", "base32-geohash", "base32-crockford"])
main32 = main(32, "RFC 4648")
main32hex = main(32, "RFC 4648", "hex", False)
main32geo = main(32, "<https://en.wikipedia.org/wiki/Geohash>", "geohash", False)
main32crk = main(32, "<https://www.crockford.com/base32.html>", "crockford", False)
mainz32 = main(32, "<https://philzimmermann.com/docs/human-oriented-base-32-encoding.txt>", "z", False)


B36 = {'': digits + upper, '[-_]inv(erted)?$': upper + digits}
base(B36, r"^base[-_]?36(|[-_]inv(?:erted)?)$")
main36 = main(36, "<https://en.wikipedia.org/wiki/Base36>")


B58 = {
    r'(|[-_]?(bc|bitcoin))$':              "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz",
    r'[-_]?(rp|ripple)$':                  "rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz",
    r'[-_]?(fl|flickr|short[-]?url|url)$': "123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ",
}
base(B58, r"^base[-_]?58(|[-_](bc|bitcoin|rp|ripple|fl|flickr|short[-]?url|url))$",
     guess=["base58-bitcoin", "base58-ripple", "base58-flickr"])
main58bc = main(58, "<https://en.bitcoinwiki.org/wiki/Base58>", "bitcoin")
main58rp = main(58, "<https://en.bitcoinwiki.org/wiki/Base58>", "ripple")
main58fl = main(58, "<https://en.bitcoinwiki.org/wiki/Base58>", "flickr")


B62 = {'': digits + upper + lower, '[-_]inv(erted)?$': upper + lower + digits}
base(B62, r"^base[-_]?62(|[-_]inv(?:erted)?)$")
main62 = main(62, "<https://en.wikipedia.org/wiki/Base62>")


B63 = {'': digits + upper + lower + "_", 'inv': upper + lower + digits + "_"}
base(B63, r"^base[-_]?63(|[-_]inv(?:erted)?)$")
main63 = main(63)


B64 = {
    r'':                        upper + lower + digits + "+/",
    r'[-_]inv(erted)?$':        digits + upper + lower + "+/",
    r'[-_]?(file|url)(safe)?$': upper + lower + digits + "-_",
}
base2n(B64, r"^base[-_]?64(|[-_]inv(?:erted)?|[-_]?(?:file|url)(?:safe)?)$", padding_char="=",
       guess=["base64", "base64-inv", "base64-url"])
main64 = main(64, "RFC 4648")
main64url = main(64, "RFC 4648 / Base64URL", "url", False)


B67 = {
    r'':                 upper + lower + digits + "-_.!~",
    r'[-_]inv(erted)?$': lower + upper + digits + "-_.!~",
}
base(B67, r"^base[-_]?67(|[-_]inv(?:erted)?)$")
main67 = main(67)


B128 = {r'': "".join(chr(i) for i in range(128))}
base(B128, r"^base[-_]?128$", padding_char="=")
main128 = main(128, None, False, wrap=False)


# generic base encodings, to be added after all others as they have the precedence
base_generic()

