`codext` provides hash functions through the `.encode(...)` API for convenience (e.g. while chaining codecs with [the CLI tool](../cli.html)).

-----

### BLAKE

These one-way transformation functions all rely on the native [`hashlib`](https://docs.python.org/3/library/hashlib.html) library.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`blake2b` | data --> Blake2b(data, length) |  | Python3 only, parametrized ; *length* belongs to [1,64]
`blake2s` | data --> Blake2s(data, length) |  | Python3 only, parametrized ; *length* belongs to [1,32]

```python
>>> codext.encode("this is a test", "blake2b")
'61a548f2de1c318ba91d5207007861010f69a43ec663fe487d8403282c934ea725dc0bb172256ac99625ad64cca6a2c4d61c650a35afab4787dc678e19071ef9'
>>> codext.encode("this is a test", "blake2s")
'f20146c054f9dd6b6764b6c09357f7cd7551dfbcba545972a4c8166df8afde60'
```

-----

### Checksums

These one-way transformation functions are mostly computed with a generic CRC.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`adler32` | data --> Adler32(data) |  | relies on [`zlib`](https://docs.python.org/3/library/zlib.html)
`crcN` | data --> CRCN(data) | many available variants ; see [this source](https://github.com/dhondta/python-codext/blob/master/codext/hashing/checksums.py) | 

```python
>>> codext.encode("This is a test string !", "crc10-gsm")
'187'
>>> codext.encode("This is a test string !", "crc14-gsm")
'0ef2'
>>> codext.encode("This is a test string !", "crc16-profibus")
'a865'
>>> codext.encode("This is a test string !", "crc30")
'2a179ad0'
>>> codext.encode("This is a test string !", "crc32-autosar")
'acfc9276'
>>> codext.encode("This is a test string !", "crc40-gsm")
'b6732ce009'
>>> codext.encode("This is a test string !", "crc64")
'e89b72737a60f502'
>>> codext.encode("This is a test string !", "crc82-darc")
'37a49332f8907c01de3d8'
```

-----

### Crypt

This one-way transformation function relies on the native [`crypt`](https://docs.python.org/3/library/crypt.html) library.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`crypt` | data --> Crypt(data, method) | `crypt-blowfish`, `crypt_md5`, ... | Python3 and Unix only, parametrized ; *method* is one of the `METHOD_[...]` values implemented in the `crypt` module for generating a salt.

```python
>>> codext.encode("This is a test string !", "crypt")
'$2b$12$xBIgGvCjYxIZ4ymKtstID.Wmf8eESVVMNU2DClPKVU37LQ5OdfUBy'
>>> codext.encode("This is a test string !", "crypt_md5")
'$1$qLvI5Kml$kXm7/Yvm87XcnzDdAgfsX1'
>>> codext.encode("This is a test string !", "crypt-sha512")
'$6$P9pjfscoLy9vpRrH$KHuRMbAltdkIQ/XL9HqrRRQTZUB2jFucH21RPbDXlsNV/ffek9MFJVZ0P2qZMTxL8m1MO0rS8UQgxj2x/Xs9A1'
```

-----

### Message Digest

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`md2` | data --> MD2(data) |  | 
`md4` | data --> MD4(data) |  | relies on [`hashlib`](https://docs.python.org/3/library/hashlib.html)
`md5` | data --> MD5(data) |  | relies on [`hashlib`](https://docs.python.org/3/library/hashlib.html)

```python
>>> codext.encode("This is a test string !", "md2")
'5200e226ea210b854974c7781b3b20d6'
>>> codext.encode("This is a test string !", "md4")
'ee4170b214eaac5be6a13d64a31b60b3'
>>> codext.encode("This is a test string !", "md5")
'5ba93d5b8e8efd9135f0030c978dd64e'
```

-----

### Secure Hash Algorithm

These one-way transformation functions all rely on the native [`hashlib`](https://docs.python.org/3/library/hashlib.html) library.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`sha1` | data --> SHA1(data) |  | 
`sha224` | data --> SHA224(data) |  | 
`sha256` | data --> SHA256(data) |  | 
`sha384` | data --> SHA384(data) |  | 
`sha3_224` | data --> SHA3-224(data) |  | Python3 only
`sha3_256` | data --> SHA3-256(data) |  | Python3 only
`sha3_384` | data --> SHA3-384(data) |  | Python3 only
`sha3_512` | data --> SHA3-512(data) |  | Python3 only
`sha512` | data --> SHA512(data) |  | 

```python
>>> codext.encode("This is a test string !", "shake_256_64")
'01a14a746d7c1d28927fe6078fdb9dcc8fabc45da58b3d1af13175b6278a6e824241927c47b4c5ced2ff629833574c9d985410d97c5c3d54d0f15b548cf2713d'
>>> codext.encode("This is a test string !", "sha224")
'85fbf14cc6e3637c303999c18f9ac3209405f4d7a11cabca8c67d0da'
>>> codext.encode("This is a test string !", "sha512")
'125683c8e8d252c753b7d1fd9bd224c638bc4b9c0311bf4173b404f1b1097a805a74d575b2a2704305e1317eafe0a1c821c54d63155f5e727c8e67ffdd3c42ab'
>>> codext.encode("This is a test string !", "sha3_384")
'f0947477521346fb9cad9d816b19a1ba0bbe2e9315faf486eeed160f5f0e8c3b78bc27d189e76e91b327ccec88938efd'
```

-----

### SHAKE

These one-way transformation functions rely on the native [`hashlib`](https://docs.python.org/3/library/hashlib.html) library.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`shake_128` | data --> Shake128(data, length) |  | Python3 only, parametrized ; *length* belongs to [1,[
`shake_256` | data --> Shake256(data, length) |  | Python3 only, parametrized ; *length* belongs to [1,[

```python
>>> codext.encode("This is a test string !", "shake_128")
'c43c192074c7d2e3e4a2c21e8f9b1bc5129b00d4c3dfa6a6fc55eba7aed13d5afd110db5bffede68496477b40f405da696dfb8e7182ca05e83ee5d301ac2f0b1b516df2d3c694f8e5c26b0d23122869130e09f705a2d59296c4de68c8632d2836952c869e5e015e9f3b3f9d83a09877d00224bebece7ac2bd6ffd11325e63b84'
>>> codext.encode("This is a test string !", "shake_128-16")
'c43c192074c7d2e3e4a2c21e8f9b1bc5'
>>> codext.encode("This is a test string !", "shake_256")
'01a14a746d7c1d28927fe6078fdb9dcc8fabc45da58b3d1af13175b6278a6e824241927c47b4c5ced2ff629833574c9d985410d97c5c3d54d0f15b548cf2713dc7c8d5145a74f6c5d613d769c03bd315350121f164f8b059fbd34548d5c1808e975858d5ea4b6edb889381a712d03954e04eacd8a077d016d8994610e9663058bef533bc71d38cb71974c7ef8abb9d2c7a0c4dfb7d007811375da4da526e37c101cead641b81faf51097b607aa3c410274074825a99d1f2a598acff414b8320be6104887c6f8df0e66aa16286da3b043cabeb90bd001e7512169c41ef8ad502666358bc7a2ea30d40a9e597dcc569cf5f8b3d383ed7c72690aca893be2ffb104'
>>> codext.encode("This is a test string !", "shake_256_64")
'01a14a746d7c1d28927fe6078fdb9dcc8fabc45da58b3d1af13175b6278a6e824241927c47b4c5ced2ff629833574c9d985410d97c5c3d54d0f15b548cf2713d'
```

