`codext` provides hash functions through the `.encode(...)` API for convenience (e.g. while chaining codecs with [the CLI tool](../cli.md)).

-----

### Argon2

These one-way transformation functions compute the Argon2 password hash ([RFC 9106](https://datatracker.ietf.org/doc/html/rfc9106)), the memory-hard winner of the Password Hashing Competition, with its three variants (Argon2d, Argon2i and the default Argon2id). A random salt is generated each time. It relies on the [`argon2-cffi`](https://pypi.org/project/argon2-cffi/) package (`pip install codext[argon2]`) and is not available without it.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`argon2` | data --> Argon2(data) | `argon2i`, `argon2d`, `argon2id` | parametrized with the variant ; random salt

```python
>>> codext.encode("test", "argon2i")[:24]
'$argon2i$v=19$m=65536,t'
```

-----

### Bcrypt

This one-way transformation function is the password hash based on the Blowfish cipher, written in the modular crypt format (`$2b$<cost>$<salt><digest>`). A random salt is generated each time, hence the output differs between calls. It relies on the [`bcrypt`](https://pypi.org/project/bcrypt/) package when it is installed (`pip install codext[bcrypt]`), and on a pure Python implementation otherwise, which is much slower (a cost of 12 takes about 40 seconds).

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`bcrypt` | data --> Bcrypt(data, cost) | `bcrypt-10`, `bcrypt_12`, ... | parametrized ; *cost* belongs to [4,31] (default: 12) ; passwords are truncated to 72 bytes

```python
>>> codext.encode("This is a test string !", "bcrypt-4")
'$2b$04$Ad./eDM.6uhky8RUAQzhiuDO.1lrx4G1lX777EtSGJAp47yU1RsN2'
```

-----

### BLAKE

These one-way transformation functions rely on the native [`hashlib`](https://docs.python.org/3/library/hashlib.html) library, except SHA-0 (withdrawn shortly after its publication and replaced by SHA-1), which is implemented in pure Python.

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
`fletcherN` | data --> FletcherN(data) | `fletcher-16`, `fletcher_32`, ... | *N* belongs to {16, 32, 64} (default: 16) ; blocks of N/2 bits are read in little-endian order

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
>>> codext.encode("This is a test string !", "fletcher")
'4ef4'
>>> codext.encode("This is a test string !", "fletcher64")
'22df63cbdafbf924'
```

-----

### Cisco PIX/ASA

These one-way transformation functions compute the password hashes of the Cisco PIX and ASA firewalls: the MD5 digest of the password (optionally salted with the user name), with every fourth byte dropped, written with the `./0-9A-Za-z` alphabet. The user name, when there is one, is given with the codec name.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`cisco-pix` | data --> PIX(data, user) | `cisco-pix-admin`, ... | parametrized with the user name (optional)
`cisco-asa` | data --> ASA(data, user) | `cisco-asa-admin`, ... | parametrized with the user name (optional)

```python
>>> codext.encode("password", "cisco-asa")
'NuLKvvWGg.x9HEKO'
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

### Crypt Variants

These one-way transformation functions compute the traditional crypt(3) password hash variants not provided by the `crypt` module (hence available on every platform): `bigcrypt` and `crypt16` (DES-based, for long passwords), `bsdi-crypt` (the extended DES scheme of BSDi, with a configurable number of rounds), `bsd-nthash` (the NT hash in the `$3$$` modular crypt format) and `sun-md5-crypt` (the MD5-based scheme of Solaris). A random salt is generated each time (except for `bsd-nthash`).

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`bigcrypt` | data --> bigcrypt(data) |  | random salt
`crypt16` | data --> crypt16(data) | `crypt-16` | random salt
`bsdi-crypt` | data --> BSDi(data, rounds) | `bsdi-crypt-5001`, ... | parametrized with the rounds (default: 5001)
`bsd-nthash` | data --> NT(data) | `bsd-nt` | 
`sun-md5-crypt` | data --> SunMD5(data, rounds) | `sun-md5-crypt-5000`, ... | parametrized with the rounds (default: 34000)

```python
>>> codext.encode("password", "bsd-nthash")
'$3$$8846f7eaee8fb117ad06bdd830b7586c'
```

-----

### CTPH

These one-way transformation functions compute context triggered piecewise hashes (aka fuzzy hashes), for which similar inputs give similar hashes: the data is split where a rolling hash of the last 7 bytes hits a trigger value depending on a block size, and each piece gives one Base64 character. `ssdeep` gives the hash of [ssdeep](https://ssdeep-project.github.io/ssdeep/) (`blocksize:hash1:hash2`), while `ctph` gives the variant of the [ctph.js](https://github.com/huwenshuo/ctph.js) library used by CyberChef's "CTPH" operation (larger minimum block size, hashes not truncated and block size written as the Base64 character of its exponent).

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`ssdeep` | data --> ssdeep(data) |  | same output as libfuzzy
`ctph` | data --> CTPH(data) |  | same output as ctph.js

```python
>>> codext.encode("This is a test string !", "ssdeep")
'3:hMCEpFZnn:hurJn'
>>> codext.encode("This is a test string !", "ctph")
'A:4NUFkERB:4BMR'
```

-----

### Fowler-Noll-Vo

These one-way transformation functions are non-cryptographic hashes, used e.g. in hash tables.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`fnv1` | data --> FNV-1(data, width) | `fnv-1`, `fnv1-64`, `fnv_1_128`, ... | parametrized ; *width* belongs to {32, 64, 128, 256, 512, 1024} (default: 32)
`fnv1a` | data --> FNV-1a(data, width) | `fnv-1a`, `fnv1a-64`, `fnv_1a_128`, ... | parametrized ; *width* belongs to {32, 64, 128, 256, 512, 1024} (default: 32)

```python
>>> codext.encode("This is a test string !", "fnv1")
'cb19f818'
>>> codext.encode("This is a test string !", "fnv1a")
'0932265e'
>>> codext.encode("This is a test string !", "fnv1a-64")
'0043c18797567d7e'
```

-----

### GOST Hash (Streebog)

This one-way transformation function is the hash function of the Russian standard GOST R 34.11-2012 ([RFC 6986](https://datatracker.ietf.org/doc/html/rfc6986)), aka Streebog, with 256-bit and 512-bit digests. The digest is written in the byte order of the usual implementations (e.g. CyberChef's), which is the reverse of the order of the examples of RFC 6986.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`gosthash` | data --> Streebog(data, size) | `gosthash-512`, `streebog`, `streebog256`, ... | parametrized ; *size* is 256 or 512 (default: 256)

```python
>>> codext.encode("This is a test string !", "gosthash")
'f9c4958ab2b57204d604e4988550e820168f14bc22e1f1150e29134670557fd1'
>>> codext.encode("This is a test string !", "streebog-512")
'a1cdee74fcdca2677e2fe47dab40be9409b5f243d0c97677ab64e93e2b0ef22e4d8f3085fd6b43ecc82e35e0a14fab29b8bdd3e1e4b2046f1be6c1ee690f372f'
```

-----

### HMAC

This one-way transformation function computes keyed-hash message authentication codes ([RFC 2104](https://datatracker.ietf.org/doc/html/rfc2104)) with the hash functions guaranteed by `hashlib` (MD5, SHA-1, SHA-2, SHA-3 and BLAKE2). The hash function and the key (as text, possibly empty) are given in the codec name.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`hmac` | data --> HMAC(hash, key, data) | `hmac-sha256-secret`, `hmac_sha3-512_key`, ... | parametrized ; *hash* among `md5`, `sha1`, `sha224`, `sha256`, `sha384`, `sha512`, `sha3-224`, `sha3-256`, `sha3-384`, `sha3-512`, `blake2b` and `blake2s`

```python
>>> codext.encode("what do ya want for nothing?", "hmac-sha256-Jefe")
'5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843'
```

-----

### Keccak

This one-way transformation function is the original Keccak, as submitted to the SHA-3 competition: it only differs from SHA-3 by the padding of the data (e.g. Ethereum uses Keccak-256).

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`keccak` | data --> Keccak(data, size) | `keccak224`, `keccak-256`, `keccak_512`, ... | parametrized ; *size* belongs to {224, 256, 384, 512} (default: 256)

```python
>>> codext.encode("This is a test string !", "keccak")
'cee1238ea4e44163d88c21979e42fedb5451d60c1f97b0221f757c1e77b37883'
>>> codext.encode("This is a test string !", "keccak-512")
'd5cbccbd447103a06c2fd3fb3b566373395ce9c573015d83d5b75f518c92ca013fc73130bf0e941d29d2283176f1816f658064ff2ee09b470e314e1d61bda761'
```

-----

### LDAP

These one-way transformation functions compute the RFC 2307 password schemes used by LDAP directories: a scheme name followed by the Base64 digest of the password, the salted variants (`{SMD5}` and `{SSHA}`) appending a random salt.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`ldap-md5` | data --> {MD5}(data) | `ldap_md5` | 
`ldap-sha1` | data --> {SHA}(data) | `ldap_sha1` | 
`ldap-salted-md5` | data --> {SMD5}(data) | `ldap-smd5` | random salt
`ldap-salted-sha1` | data --> {SSHA}(data) | `ldap-ssha` | random salt

```python
>>> codext.encode("password", "ldap-md5")
'{MD5}X03MO1qnZdYdgyfeuILPmQ=='
```

-----

### Message Digest

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`md2` | data --> MD2(data) |  | 
`md4` | data --> MD4(data) |  | relies on [`hashlib`](https://docs.python.org/3/library/hashlib.html) when available, pure Python otherwise
`md5` | data --> MD5(data) |  | relies on [`hashlib`](https://docs.python.org/3/library/hashlib.html)
`md6` | data --> MD6(data, size) | `md6-128`, `md6_512`, ... | parametrized ; *size* is a multiple of 8 in [8, 512] (default: 256) ; unkeyed, with the default tree height (64)

```python
>>> codext.encode("This is a test string !", "md2")
'5200e226ea210b854974c7781b3b20d6'
>>> codext.encode("This is a test string !", "md4")
'ee4170b214eaac5be6a13d64a31b60b3'
>>> codext.encode("This is a test string !", "md5")
'5ba93d5b8e8efd9135f0030c978dd64e'
>>> codext.encode("This is a test string !", "md6")
'dc29b9f3d9cd16cf27b71f915b386bdd8fc3daa5eb7476a3408442d52bf8d869'
>>> codext.encode("This is a test string !", "md6-128")
'091d9f116b997823999ac64cfe3bfbad'
```

-----

### MS-CASH

These one-way transformation functions compute the Windows domain cached credentials (Domain Cached Credentials): MS-CASHv1 (the MD4 digest of the NT hash and the lowercased user name) and MS-CASHv2 (PBKDF2-HMAC-SHA1 over it). The user name (the salt) is given with the codec name.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`mscash` | data --> MSCASHv1(data, user) | `mscash1`, `ms-cash` | parametrized with the user name
`mscash2` | data --> MSCASHv2(data, user) | `ms-cash2` | parametrized with the user name

```python
>>> codext.encode("password", "mscash-Administrator")
'25fd08fa89795ed54207e6e8442a6ca0'
```

-----

### MSSQL

These one-way transformation functions compute the Microsoft SQL Server password hashes: `0x0100`, a 4-byte random salt and the SHA-1 digest of the salted password (encoded in UTF-16LE). The 2000 version appends a second digest of the uppercased password ; the 2005 version drops it.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`mssql2000` | data --> MSSQL2000(data) | `mssql-2000` | random salt
`mssql2005` | data --> MSSQL2005(data) | `mssql-2005` | random salt

```python
>>> codext.encode("test", "mssql2005")[:14]
'0x0100'  # + salt and digest in hexadecimal
```

-----

### MySQL

These one-way transformation functions compute the password hashes of MySQL: the custom 64-bit hash of MySQL 3.23 (spaces and tabs being ignored) and the native password hash of MySQL 4.1 and later (SHA-1 of the binary SHA-1 digest).

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`mysql323` | data --> MySQL323(data) | `mysql-3.23`, `mysql3` | 
`mysql41` | data --> MySQL41(data) | `mysql-4.1`, `mysql4` | uppercase digest prefixed with `*`, as stored by MySQL

```python
>>> codext.encode("This is a test string !", "mysql323")
'19a9b4171de94050'
>>> codext.encode("This is a test string !", "mysql41")
'*43782A96DB4DB788BFF188B26F633AFB47FDA7D0'
```

-----

### Oracle

These one-way transformation functions compute the Oracle database password hashes: the legacy 10g hash (DES-CBC of the uppercased user name and password) and the 11g hash (`S:`, the SHA-1 digest of the password and a random 10-byte salt). The user name of the 10g hash (the salt) is given with the codec name.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`oracle10` | data --> Oracle10g(data, user) | `oracle-10g-SYSTEM`, ... | parametrized with the user name
`oracle11` | data --> Oracle11g(data) | `oracle-11g` | random salt

```python
>>> codext.encode("password", "oracle10-SYSTEM")
'EED9B65CCECDB2E9'
```

-----

### PHPass

These one-way transformation functions compute the portable PHP password hash (used e.g. by WordPress): `$P$`, an iteration count and an 8-character random salt, followed by the iterated MD5 digest. The iteration count (a power of 2, from 7 to 30) is given with the codec name (default: 13).

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`phpass` | data --> PHPass(data) | `phpass-13`, `phpass_20`, ... | parametrized ; random salt

```python
>>> codext.encode("password", "phpass")[:3]
'$P$'
```

-----

### RIPEMD

This one-way transformation function, used e.g. in Bitcoin addresses, relies on [`hashlib`](https://docs.python.org/3/library/hashlib.html) when it provides it, and on a pure Python implementation otherwise (OpenSSL 3 only provides it in its legacy provider).

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`ripemd160` | data --> RIPEMD-160(data) | `ripemd-160`, `rmd160`, ... | 

```python
>>> codext.encode("This is a test string !", "ripemd160")
'f0c90bd665512fc158f3c47d6de76b58783c404c'
```

-----

### Secure Hash Algorithm

These one-way transformation functions rely on the native [`hashlib`](https://docs.python.org/3/library/hashlib.html) library, except SHA-0 (withdrawn shortly after its publication and replaced by SHA-1), which is implemented in pure Python.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`sha0` | data --> SHA0(data) |  | 
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
>>> codext.encode("This is a test string !", "sha0")
'2cffee460320a8c226b9a62819f9409367d97e1b'
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

-----

### Snefru

This one-way transformation function, designed by Ralph Merkle in 1990, is implemented in pure Python. Its number of passes was raised from 2 to 8 after it was broken with differential cryptanalysis ; PHP's `snefru` is `snefru-256` (with 8 passes), while CyberChef defaults to `snefru` (128 bits).

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`snefru` | data --> Snefru(data, size, passes) | `snefru128`, `snefru-256`, `snefru_256_4`, ... | parametrized ; *size* is a multiple of 32 from 32 to 480 (default: 128) and *passes* belongs to [2,8] (default: 8)

```python
>>> codext.encode("This is a test string !", "snefru")
'b4c5c863defc053ad15be9bc01609c57'
>>> codext.encode("This is a test string !", "snefru-256")
'ba1e1a138b432e94547c46aaf5fd4851651d1ab75da937cd4cf349a02961edf4'
>>> codext.encode("This is a test string !", "snefru-256-4")
'6c6e9478662fe169dfb487af98e1667644cac8f3c5eadba5fbd437bfdf5c1f1a'
```

-----

### Whirlpool

This one-way transformation function, adopted in ISO/IEC 10118-3, relies on [`hashlib`](https://docs.python.org/3/library/hashlib.html) when it provides it, and on a pure Python implementation otherwise (OpenSSL 3 only provides it in its legacy provider).

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`whirlpool` | data --> Whirlpool(data) |  | 

```python
>>> codext.encode("This is a test string !", "whirlpool")
'60c9fe1d138fcf42d73798223394d0decebb60b170b5250fd0d18116a9f5d9a0c183220315a65d2fe0c9c4f5a5c314949b64581b9928fa32462b4b3a7b096798'
```

-----

### Windows

These one-way transformation functions compute the password hashes of Windows: the legacy LAN Manager (LM) hash (uppercased password, truncated to 14 characters, whose halves are DES keys encrypting `KGS!@#$%` ; DES is implemented in pure Python) and the NT hash, i.e. the MD4 digest of the password encoded in UTF-16LE.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`lm` | data --> LM(data) | `lmhash`, `lm-hash` | 
`ntlm` | data --> NT(data) | `nt`, `nthash`, `nt-hash` | 

```python
>>> codext.encode("This is a test string !", "lm")
'62b4f4e39b2ef8637f8e43d4eb012c81'
>>> codext.encode("This is a test string !", "ntlm")
'9749468129a3b135d63d3371504d6d12'
```
