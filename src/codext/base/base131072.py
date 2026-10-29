# -*- coding: UTF-8 -*-
"""Base131072 Codec - base131072 content encoding.

Base131072 writes the data with 17 bits per character. Its design by qntm (as a successor of Base65536) was never
 completed as its repertoire was never defined ; this codec implements the variant of the "base131072" Rust crate,
 whose repertoire holds the first 131072 assigned code points of Unicode 13.0 (from U+0020, hence including the
 printable ASCII characters and the space).

The bits are taken most significant first, the final bits being padded with 0s up to 17 bits. As the 17-bit groups
 decode to whole bytes, possibly 1 or 2 more than the data, a last character tells how many bytes must be dropped when
 decoding: U+2EA39 for 1 byte and U+2EA38 for 2 bytes. When decoding, tabs and newlines are ignored.

This codec:
- en/decodes strings from str to str
- en/decodes strings from bytes to bytes
- decodes file content to str (read)
- encodes file content from str to bytes (write)

Reference: https://docs.rs/base131072/latest/src/base131072/lib.rs.html
"""
from functools import lru_cache

from ._base import main
from ..__common__ import *


# NB: short random strings may be valid UTF-8 once converted to bytes, then read as text by codext ; hence, fixed
#      strings holding "\xff" are used for the round trips
__examples__ = {
    'enc(base131072|base-131072|base_131072)': {'': "", '\x01': "\u0241\U0002ea38", '\x01\x02': "\u0245\U0002ea39",
                                                '\x01\x02\x03': "\u0245\u0e09\U0002ea38"},
    'dec(base131072)':     {'\u0241\U0002ea38': "\x01", '\u0245\n\u0e09\U0002ea38': "\x01\x02\x03",
                            '\u0241\u0241': None, '\u0241': None, '\u0242\U0002ea38': None, '\U0002ea38': None,
                            '\U0002ea38\u0241': None, '\u0241\x00': None},
    'enc-dec(base131072)': ["\xff", "\xff\xfe", "A\xff\x80", "\xffbcd", "\xff" * 17, "Hello, World!",
                            "@random{512,1024}"],
}
__guess__ = ["base131072"]


# repertoire as inclusive ranges of code points (hexadecimal) and padding characters (for 1 and 2 bytes)
REPERTOIRE = (
    "20-7e a0-377 37a-37f 384-38a 38c-38c 38e-3a1 3a3-52f 531-556 559-58a 58d-58f 591-5c7 5d0-5ea 5ef-5f4 "
    "600-61c 61e-70d 70f-74a 74d-7b1 7c0-7fa 7fd-82d 830-83e 840-85b 85e-85e 860-86a 8a0-8b4 8b6-8c7 8d3-983 "
    "985-98c 98f-990 993-9a8 9aa-9b0 9b2-9b2 9b6-9b9 9bc-9c4 9c7-9c8 9cb-9ce 9d7-9d7 9dc-9dd 9df-9e3 9e6-9fe "
    "a01-a03 a05-a0a a0f-a10 a13-a28 a2a-a30 a32-a33 a35-a36 a38-a39 a3c-a3c a3e-a42 a47-a48 a4b-a4d a51-a51 "
    "a59-a5c a5e-a5e a66-a76 a81-a83 a85-a8d a8f-a91 a93-aa8 aaa-ab0 ab2-ab3 ab5-ab9 abc-ac5 ac7-ac9 acb-acd "
    "ad0-ad0 ae0-ae3 ae6-af1 af9-aff b01-b03 b05-b0c b0f-b10 b13-b28 b2a-b30 b32-b33 b35-b39 b3c-b44 b47-b48 "
    "b4b-b4d b55-b57 b5c-b5d b5f-b63 b66-b77 b82-b83 b85-b8a b8e-b90 b92-b95 b99-b9a b9c-b9c b9e-b9f ba3-ba4 "
    "ba8-baa bae-bb9 bbe-bc2 bc6-bc8 bca-bcd bd0-bd0 bd7-bd7 be6-bfa c00-c0c c0e-c10 c12-c28 c2a-c39 c3d-c44 "
    "c46-c48 c4a-c4d c55-c56 c58-c5a c60-c63 c66-c6f c77-c8c c8e-c90 c92-ca8 caa-cb3 cb5-cb9 cbc-cc4 cc6-cc8 "
    "cca-ccd cd5-cd6 cde-cde ce0-ce3 ce6-cef cf1-cf2 d00-d0c d0e-d10 d12-d44 d46-d48 d4a-d4f d54-d63 d66-d7f "
    "d81-d83 d85-d96 d9a-db1 db3-dbb dbd-dbd dc0-dc6 dca-dca dcf-dd4 dd6-dd6 dd8-ddf de6-def df2-df4 e01-e3a "
    "e3f-e5b e81-e82 e84-e84 e86-e8a e8c-ea3 ea5-ea5 ea7-ebd ec0-ec4 ec6-ec6 ec8-ecd ed0-ed9 edc-edf f00-f47 "
    "f49-f6c f71-f97 f99-fbc fbe-fcc fce-fda 1000-10c5 10c7-10c7 10cd-10cd 10d0-1248 124a-124d 1250-1256 "
    "1258-1258 125a-125d 1260-1288 128a-128d 1290-12b0 12b2-12b5 12b8-12be 12c0-12c0 12c2-12c5 12c8-12d6 "
    "12d8-1310 1312-1315 1318-135a 135d-137c 1380-1399 13a0-13f5 13f8-13fd 1400-169c 16a0-16f8 1700-170c "
    "170e-1714 1720-1736 1740-1753 1760-176c 176e-1770 1772-1773 1780-17dd 17e0-17e9 17f0-17f9 1800-180e "
    "1810-1819 1820-1878 1880-18aa 18b0-18f5 1900-191e 1920-192b 1930-193b 1940-1940 1944-196d 1970-1974 "
    "1980-19ab 19b0-19c9 19d0-19da 19de-1a1b 1a1e-1a5e 1a60-1a7c 1a7f-1a89 1a90-1a99 1aa0-1aad 1ab0-1ac0 "
    "1b00-1b4b 1b50-1b7c 1b80-1bf3 1bfc-1c37 1c3b-1c49 1c4d-1c88 1c90-1cba 1cbd-1cc7 1cd0-1cfa 1d00-1df9 "
    "1dfb-1f15 1f18-1f1d 1f20-1f45 1f48-1f4d 1f50-1f57 1f59-1f59 1f5b-1f5b 1f5d-1f5d 1f5f-1f7d 1f80-1fb4 "
    "1fb6-1fc4 1fc6-1fd3 1fd6-1fdb 1fdd-1fef 1ff2-1ff4 1ff6-1ffe 2000-2064 2066-2071 2074-208e 2090-209c "
    "20a0-20bf 20d0-20f0 2100-218b 2190-2426 2440-244a 2460-2b73 2b76-2b95 2b97-2c2e 2c30-2c5e 2c60-2cf3 "
    "2cf9-2d25 2d27-2d27 2d2d-2d2d 2d30-2d67 2d6f-2d70 2d7f-2d96 2da0-2da6 2da8-2dae 2db0-2db6 2db8-2dbe "
    "2dc0-2dc6 2dc8-2dce 2dd0-2dd6 2dd8-2dde 2de0-2e52 2e80-2e99 2e9b-2ef3 2f00-2fd5 2ff0-2ffb 3000-303f "
    "3041-3096 3099-30ff 3105-312f 3131-318e 3190-31e3 31f0-321e 3220-9ffc a000-a48c a490-a4c6 a4d0-a62b "
    "a640-a6f7 a700-a7bf a7c2-a7ca a7f5-a82c a830-a839 a840-a877 a880-a8c5 a8ce-a8d9 a8e0-a953 a95f-a97c "
    "a980-a9cd a9cf-a9d9 a9de-a9fe aa00-aa36 aa40-aa4d aa50-aa59 aa5c-aac2 aadb-aaf6 ab01-ab06 ab09-ab0e "
    "ab11-ab16 ab20-ab26 ab28-ab2e ab30-ab6b ab70-abed abf0-abf9 ac00-ac1a ac1c-ac36 ac38-ac52 ac54-ac6e "
    "ac70-ac8a ac8c-aca6 aca8-acc2 acc4-acde ace0-acfa acfc-ad16 ad18-ad32 ad34-ad4e ad50-ad6a ad6c-ad86 "
    "ad88-ada2 ada4-adbe adc0-adda addc-adf6 adf8-ae12 ae14-ae2e ae30-ae4a ae4c-ae66 ae68-ae82 ae84-ae9e "
    "aea0-aeba aebc-aed6 aed8-aef2 aef4-af0e af10-af2a af2c-af46 af48-af62 af64-af7e af80-af9a af9c-afb6 "
    "afb8-afd2 afd4-afee aff0-b00a b00c-b026 b028-b042 b044-b05e b060-b07a b07c-b096 b098-b0b2 b0b4-b0ce "
    "b0d0-b0ea b0ec-b106 b108-b122 b124-b13e b140-b15a b15c-b176 b178-b192 b194-b1ae b1b0-b1ca b1cc-b1e6 "
    "b1e8-b202 b204-b21e b220-b23a b23c-b256 b258-b272 b274-b28e b290-b2aa b2ac-b2c6 b2c8-b2e2 b2e4-b2fe "
    "b300-b31a b31c-b336 b338-b352 b354-b36e b370-b38a b38c-b3a6 b3a8-b3c2 b3c4-b3de b3e0-b3fa b3fc-b416 "
    "b418-b432 b434-b44e b450-b46a b46c-b486 b488-b4a2 b4a4-b4be b4c0-b4da b4dc-b4f6 b4f8-b512 b514-b52e "
    "b530-b54a b54c-b566 b568-b582 b584-b59e b5a0-b5ba b5bc-b5d6 b5d8-b5f2 b5f4-b60e b610-b62a b62c-b646 "
    "b648-b662 b664-b67e b680-b69a b69c-b6b6 b6b8-b6d2 b6d4-b6ee b6f0-b70a b70c-b726 b728-b742 b744-b75e "
    "b760-b77a b77c-b796 b798-b7b2 b7b4-b7ce b7d0-b7ea b7ec-b806 b808-b822 b824-b83e b840-b85a b85c-b876 "
    "b878-b892 b894-b8ae b8b0-b8ca b8cc-b8e6 b8e8-b902 b904-b91e b920-b93a b93c-b956 b958-b972 b974-b98e "
    "b990-b9aa b9ac-b9c6 b9c8-b9e2 b9e4-b9fe ba00-ba1a ba1c-ba36 ba38-ba52 ba54-ba6e ba70-ba8a ba8c-baa6 "
    "baa8-bac2 bac4-bade bae0-bafa bafc-bb16 bb18-bb32 bb34-bb4e bb50-bb6a bb6c-bb86 bb88-bba2 bba4-bbbe "
    "bbc0-bbda bbdc-bbf6 bbf8-bc12 bc14-bc2e bc30-bc4a bc4c-bc66 bc68-bc82 bc84-bc9e bca0-bcba bcbc-bcd6 "
    "bcd8-bcf2 bcf4-bd0e bd10-bd2a bd2c-bd46 bd48-bd62 bd64-bd7e bd80-bd9a bd9c-bdb6 bdb8-bdd2 bdd4-bdee "
    "bdf0-be0a be0c-be26 be28-be42 be44-be5e be60-be7a be7c-be96 be98-beb2 beb4-bece bed0-beea beec-bf06 "
    "bf08-bf22 bf24-bf3e bf40-bf5a bf5c-bf76 bf78-bf92 bf94-bfae bfb0-bfca bfcc-bfe6 bfe8-c002 c004-c01e "
    "c020-c03a c03c-c056 c058-c072 c074-c08e c090-c0aa c0ac-c0c6 c0c8-c0e2 c0e4-c0fe c100-c11a c11c-c136 "
    "c138-c152 c154-c16e c170-c18a c18c-c1a6 c1a8-c1c2 c1c4-c1de c1e0-c1fa c1fc-c216 c218-c232 c234-c24e "
    "c250-c26a c26c-c286 c288-c2a2 c2a4-c2be c2c0-c2da c2dc-c2f6 c2f8-c312 c314-c32e c330-c34a c34c-c366 "
    "c368-c382 c384-c39e c3a0-c3ba c3bc-c3d6 c3d8-c3f2 c3f4-c40e c410-c42a c42c-c446 c448-c462 c464-c47e "
    "c480-c49a c49c-c4b6 c4b8-c4d2 c4d4-c4ee c4f0-c50a c50c-c526 c528-c542 c544-c55e c560-c57a c57c-c596 "
    "c598-c5b2 c5b4-c5ce c5d0-c5ea c5ec-c606 c608-c622 c624-c63e c640-c65a c65c-c676 c678-c692 c694-c6ae "
    "c6b0-c6ca c6cc-c6e6 c6e8-c702 c704-c71e c720-c73a c73c-c756 c758-c772 c774-c78e c790-c7aa c7ac-c7c6 "
    "c7c8-c7e2 c7e4-c7fe c800-c81a c81c-c836 c838-c852 c854-c86e c870-c88a c88c-c8a6 c8a8-c8c2 c8c4-c8de "
    "c8e0-c8fa c8fc-c916 c918-c932 c934-c94e c950-c96a c96c-c986 c988-c9a2 c9a4-c9be c9c0-c9da c9dc-c9f6 "
    "c9f8-ca12 ca14-ca2e ca30-ca4a ca4c-ca66 ca68-ca82 ca84-ca9e caa0-caba cabc-cad6 cad8-caf2 caf4-cb0e "
    "cb10-cb2a cb2c-cb46 cb48-cb62 cb64-cb7e cb80-cb9a cb9c-cbb6 cbb8-cbd2 cbd4-cbee cbf0-cc0a cc0c-cc26 "
    "cc28-cc42 cc44-cc5e cc60-cc7a cc7c-cc96 cc98-ccb2 ccb4-ccce ccd0-ccea ccec-cd06 cd08-cd22 cd24-cd3e "
    "cd40-cd5a cd5c-cd76 cd78-cd92 cd94-cdae cdb0-cdca cdcc-cde6 cde8-ce02 ce04-ce1e ce20-ce3a ce3c-ce56 "
    "ce58-ce72 ce74-ce8e ce90-ceaa ceac-cec6 cec8-cee2 cee4-cefe cf00-cf1a cf1c-cf36 cf38-cf52 cf54-cf6e "
    "cf70-cf8a cf8c-cfa6 cfa8-cfc2 cfc4-cfde cfe0-cffa cffc-d016 d018-d032 d034-d04e d050-d06a d06c-d086 "
    "d088-d0a2 d0a4-d0be d0c0-d0da d0dc-d0f6 d0f8-d112 d114-d12e d130-d14a d14c-d166 d168-d182 d184-d19e "
    "d1a0-d1ba d1bc-d1d6 d1d8-d1f2 d1f4-d20e d210-d22a d22c-d246 d248-d262 d264-d27e d280-d29a d29c-d2b6 "
    "d2b8-d2d2 d2d4-d2ee d2f0-d30a d30c-d326 d328-d342 d344-d35e d360-d37a d37c-d396 d398-d3b2 d3b4-d3ce "
    "d3d0-d3ea d3ec-d406 d408-d422 d424-d43e d440-d45a d45c-d476 d478-d492 d494-d4ae d4b0-d4ca d4cc-d4e6 "
    "d4e8-d502 d504-d51e d520-d53a d53c-d556 d558-d572 d574-d58e d590-d5aa d5ac-d5c6 d5c8-d5e2 d5e4-d5fe "
    "d600-d61a d61c-d636 d638-d652 d654-d66e d670-d68a d68c-d6a6 d6a8-d6c2 d6c4-d6de d6e0-d6fa d6fc-d716 "
    "d718-d732 d734-d74e d750-d76a d76c-d786 d788-d7a2 d7b0-d7c6 d7cb-d7fb f900-fa6d fa70-fad9 fb00-fb06 "
    "fb13-fb17 fb1d-fb36 fb38-fb3c fb3e-fb3e fb40-fb41 fb43-fb44 fb46-fbc1 fbd3-fd3f fd50-fd8f fd92-fdc7 "
    "fdf0-fdfd fe00-fe19 fe20-fe52 fe54-fe66 fe68-fe6b fe70-fe74 fe76-fefc feff-feff ff01-ffbe ffc2-ffc7 "
    "ffca-ffcf ffd2-ffd7 ffda-ffdc ffe0-ffe6 ffe8-ffee fff9-fffd 10000-1000b 1000d-10026 10028-1003a "
    "1003c-1003d 1003f-1004d 10050-1005d 10080-100fa 10100-10102 10107-10133 10137-1018e 10190-1019c "
    "101a0-101a0 101d0-101fd 10280-1029c 102a0-102d0 102e0-102fb 10300-10323 1032d-1034a 10350-1037a "
    "10380-1039d 1039f-103c3 103c8-103d5 10400-1049d 104a0-104a9 104b0-104d3 104d8-104fb 10500-10527 "
    "10530-10563 1056f-1056f 10600-10736 10740-10755 10760-10767 10800-10805 10808-10808 1080a-10835 "
    "10837-10838 1083c-1083c 1083f-10855 10857-1089e 108a7-108af 108e0-108f2 108f4-108f5 108fb-1091b "
    "1091f-10939 1093f-1093f 10980-109b7 109bc-109cf 109d2-10a03 10a05-10a06 10a0c-10a13 10a15-10a17 "
    "10a19-10a35 10a38-10a3a 10a3f-10a48 10a50-10a58 10a60-10a9f 10ac0-10ae6 10aeb-10af6 10b00-10b35 "
    "10b39-10b55 10b58-10b72 10b78-10b91 10b99-10b9c 10ba9-10baf 10c00-10c48 10c80-10cb2 10cc0-10cf2 "
    "10cfa-10d27 10d30-10d39 10e60-10e7e 10e80-10ea9 10eab-10ead 10eb0-10eb1 10f00-10f27 10f30-10f59 "
    "10fb0-10fcb 10fe0-10ff6 11000-1104d 11052-1106f 1107f-110c1 110cd-110cd 110d0-110e8 110f0-110f9 "
    "11100-11134 11136-11147 11150-11176 11180-111df 111e1-111f4 11200-11211 11213-1123e 11280-11286 "
    "11288-11288 1128a-1128d 1128f-1129d 1129f-112a9 112b0-112ea 112f0-112f9 11300-11303 11305-1130c "
    "1130f-11310 11313-11328 1132a-11330 11332-11333 11335-11339 1133b-11344 11347-11348 1134b-1134d "
    "11350-11350 11357-11357 1135d-11363 11366-1136c 11370-11374 11400-1145b 1145d-11461 11480-114c7 "
    "114d0-114d9 11580-115b5 115b8-115dd 11600-11644 11650-11659 11660-1166c 11680-116b8 116c0-116c9 "
    "11700-1171a 1171d-1172b 11730-1173f 11800-1183b 118a0-118f2 118ff-11906 11909-11909 1190c-11913 "
    "11915-11916 11918-11935 11937-11938 1193b-11946 11950-11959 119a0-119a7 119aa-119d7 119da-119e4 "
    "11a00-11a47 11a50-11aa2 11ac0-11af8 11c00-11c08 11c0a-11c36 11c38-11c45 11c50-11c6c 11c70-11c8f "
    "11c92-11ca7 11ca9-11cb6 11d00-11d06 11d08-11d09 11d0b-11d36 11d3a-11d3a 11d3c-11d3d 11d3f-11d47 "
    "11d50-11d59 11d60-11d65 11d67-11d68 11d6a-11d8e 11d90-11d91 11d93-11d98 11da0-11da9 11ee0-11ef8 "
    "11fb0-11fb0 11fc0-11ff1 11fff-12399 12400-1246e 12470-12474 12480-12543 13000-1342e 13430-13438 "
    "14400-14646 16800-16a38 16a40-16a5e 16a60-16a69 16a6e-16a6f 16ad0-16aed 16af0-16af5 16b00-16b45 "
    "16b50-16b59 16b5b-16b61 16b63-16b77 16b7d-16b8f 16e40-16e9a 16f00-16f4a 16f4f-16f87 16f8f-16f9f "
    "16fe0-16fe4 16ff0-16ff1 18800-18cd5 1b000-1b11e 1b150-1b152 1b164-1b167 1b170-1b2fb 1bc00-1bc6a "
    "1bc70-1bc7c 1bc80-1bc88 1bc90-1bc99 1bc9c-1bca3 1d000-1d0f5 1d100-1d126 1d129-1d1e8 1d200-1d245 "
    "1d2e0-1d2f3 1d300-1d356 1d360-1d378 1d400-1d454 1d456-1d49c 1d49e-1d49f 1d4a2-1d4a2 1d4a5-1d4a6 "
    "1d4a9-1d4ac 1d4ae-1d4b9 1d4bb-1d4bb 1d4bd-1d4c3 1d4c5-1d505 1d507-1d50a 1d50d-1d514 1d516-1d51c "
    "1d51e-1d539 1d53b-1d53e 1d540-1d544 1d546-1d546 1d54a-1d550 1d552-1d6a5 1d6a8-1d7cb 1d7ce-1da8b "
    "1da9b-1da9f 1daa1-1daaf 1e000-1e006 1e008-1e018 1e01b-1e021 1e023-1e024 1e026-1e02a 1e100-1e12c "
    "1e130-1e13d 1e140-1e149 1e14e-1e14f 1e2c0-1e2f9 1e2ff-1e2ff 1e800-1e8c4 1e8c7-1e8d6 1e900-1e94b "
    "1e950-1e959 1e95e-1e95f 1ec71-1ecb4 1ed01-1ed3d 1ee00-1ee03 1ee05-1ee1f 1ee21-1ee22 1ee24-1ee24 "
    "1ee27-1ee27 1ee29-1ee32 1ee34-1ee37 1ee39-1ee39 1ee3b-1ee3b 1ee42-1ee42 1ee47-1ee47 1ee49-1ee49 "
    "1ee4b-1ee4b 1ee4d-1ee4f 1ee51-1ee52 1ee54-1ee54 1ee57-1ee57 1ee59-1ee59 1ee5b-1ee5b 1ee5d-1ee5d "
    "1ee5f-1ee5f 1ee61-1ee62 1ee64-1ee64 1ee67-1ee6a 1ee6c-1ee72 1ee74-1ee77 1ee79-1ee7c 1ee7e-1ee7e "
    "1ee80-1ee89 1ee8b-1ee9b 1eea1-1eea3 1eea5-1eea9 1eeab-1eebb 1eef0-1eef1 1f000-1f02b 1f030-1f093 "
    "1f0a0-1f0ae 1f0b1-1f0bf 1f0c1-1f0cf 1f0d1-1f0f5 1f100-1f1ad 1f1e6-1f202 1f210-1f23b 1f240-1f248 "
    "1f250-1f251 1f260-1f265 1f300-1f6d7 1f6e0-1f6ec 1f6f0-1f6fc 1f700-1f773 1f780-1f7d8 1f7e0-1f7eb "
    "1f800-1f80b 1f810-1f847 1f850-1f859 1f860-1f887 1f890-1f8ad 1f8b0-1f8b1 1f900-1f978 1f97a-1f9cb "
    "1f9cd-1fa53 1fa60-1fa6d 1fa70-1fa74 1fa78-1fa7a 1fa80-1fa86 1fa90-1faa8 1fab0-1fab6 1fac0-1fac2 "
    "1fad0-1fad6 1fb00-1fb92 1fb94-1fbca 1fbf0-1fbf9 20000-2a6dd 2a700-2b734 2b740-2b81d 2b820-2cea1 "
    "2ceb0-2ea37"
)
PAD = {chr(0x2ea39): 1, chr(0x2ea38): 2}


@lru_cache(maxsize=None)
def __tables():
    """ Build the repertoire and its decoding table ; this is done lazily, at first use, as it takes some tens of
         milliseconds that should not be spent when importing codext. """
    rep = "".join(chr(c) for r in REPERTOIRE.split() for a, b in [r.split("-")]
                  for c in range(int(a, 16), int(b, 16) + 1))
    return rep, {c: z for z, c in enumerate(rep)}


def base131072_encode(text, errors="strict"):
    rep, t = __tables()[0], b(text)
    r, z, k = [], 0, 0
    for x in t:
        z, k = z << 8 | x, k + 8
        if k >= 17:
            k -= 17
            r.append(rep[z >> k])
            z &= (1 << k) - 1
    if k > 0:
        # the final bits are padded with 0s up to 17 bits
        r.append(rep[z << (17 - k)])
    # the groups decode to ceil(17g/8) bytes, hence one or two additional bytes to be dropped when decoding
    p = -(-17 * len(r) // 8) - len(t)
    if p:
        r.append({1: chr(0x2ea39), 2: chr(0x2ea38)}[p])
    return (s := "".join(r)), len(s)


def base131072_decode(text, errors="strict"):
    _h, text, lookup = handle_error("base131072", errors, decode=True), ensure_str(text), __tables()[1]
    # tabs and newlines are ignored, while the space belongs to the repertoire
    chars = [(i, c) for i, c in enumerate(text) if c not in "\t\r\n"]
    r, p, g, z, k = bytearray(), 0, 0, 0, 0
    for j, (i, c) in enumerate(chars):
        if c in PAD and j == len(chars) - 1 and j > 0:
            p = PAD[c]
        elif c in lookup:
            z, k, g = z << 17 | lookup[c], k + 17, g + 1
            while k >= 8:
                k -= 8
                r.append(z >> k & 255)
            z &= (1 << k) - 1
        else:
            # a wrong character cannot be replaced in the binary stream, hence it is dropped (a padding character can
            #  only end the encoded text)
            _h(c, i)
    if k > 0:
        # the last incomplete byte, completed with 0s
        r.append(z << (8 - k))
    # the encoded text must be the one of the data: same number of groups, same padding character and null padding
    #  bits (all in the dropped bytes)
    n = max(0, len(r) - p)
    if (g != -(-8 * n // 17) or p != len(r) - n or any(r[n:])) and errors == "strict":
        handle_error("base131072", errors, decode=True, kind="padding")(text[-1:], len(text) - 1)
    return bytes(r[:n]), n


add("base131072", base131072_encode, base131072_decode, r"^base[-_]?131072$",
    # the padding character makes short encoded texts longer than expected
    expansion_factor=(8 / 17, .4))
main131072 = main(131072, "<https://docs.rs/base131072>", inv=False, swap=False, wrap=False)
