`codext` defines a far broader set of Base-encodings than in the original library.

-----

### Classical base 2^N encodings

This namely adds the classical BaseXX encodings like 16 (hexadecimal) and 32 (RFC 3548), which are not available in the native codecs.

Common base encodings with N a power of 2:

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`base2` | text <-> Base2 encoded text | `(base[-_]?2|bin)-inv(erted)?` | Dynamic charset parameter `[-_]...`, amongst letters and digits (e.g. `_AB`)
`base4` | text <-> Base4 encoded text | `base[-_]?4-inv(erted)` | Dynamic charset parameter `[-_]...`, amongst letters and digits (e.g. `_6VC9`)
`base8` | text <-> Base8 encoded text | `base[-_]?8-inv(erted)` | Charset: `abcdefgh` ; Dynamic charset parameter `[-_]...`, amongst letters and digits (e.g. `_A5c96T7x`)
`base16` | text <-> Base16 encoded text | `base[-_]?16-inv(erted)` | 
`base32` | text <-> Base32 encoded text | `base[-_]?32-inv(erted)`, `base32-crockford`, `base32_geohash`, ... | Also supports Base32 Crockford, Geohash and Hex
`zbase32` | text <-> ZBase32 encoded text | `z[-_]?base[-_]?32` | Human-oriented Base32
`base64` | text <-> Base64 encoded text | `base[-_]?64-inv(erted)` | 

!!! note "Aliases"
    
    All the aliases are case insensitive for base encodings.

```python
>>> codext.encode("test", "base2")
'01110100011001010111001101110100'
>>> codext.encode("test", "base2-inv")
'10001011100110101000110010001011'
```

```python
>>> codecs.encode("this is a test", "base16")
'7468697320697320612074657374'
>>> codecs.decode("7468697320697320612074657374", "base16")
'this is a test'
>>> codecs.encode("this is a test", "base16-inv")
'1E02031DCA031DCA0BCA1E0F1D1E'
```

```python
>>> codext.encode("this is a test", "base32")
'ORUGS4ZANFZSAYJAORSXG5A='
>>> codext.decode("ORUGS4ZANFZSAYJAORSXG5A=", "base32")
'this is a test'
```

Note that for `base64`, it overwrites the native `base64_codec` to also support en/decoding from str.

```python
>>> codecs.encode("this is a test", "base64")
'dGhpcyBpcyBhIHRlc3Q='
>>> codecs.decode("dGhpcyBpcyBhIHRlc3Q=", "base64")
'this is a test'
```

-----

### Generic base encodings

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`base3` | text <-> Base3 encoded text | `base[-_]?3(|[-_]inv(erted)?)` | Dynamic charset parameter `[-_]...`, amongst letters and digits (e.g. `_C2Z`)
`base10` | text <-> Base10 encoded text | `base[-_]?10|int(?:eger)?|dec(?:imal)?` | 
`base11` | text <-> Base11 encoded text | `base[-_]?11(|[-_]inv(erted)?)` | 
`base36` | text <-> Base36 encoded text | `base[-_]?36(|[-_]inv(erted)?)` | 
`base38` | data <-> Base38 encoded text | `base[-_]?38` | Matter QR code payload encoding (chunks of 3 bytes)
`base45` | text <-> Base45 encoded text | `base[-_]?45(|[-_]inv(erted)?)` | 
`base58` | text <-> Base58 encoded text | `base[-_]?58(|[-_](bc|bitcoin|rp|ripple|fl|flickr|short[-]?url|url))` | Supports Bitcoin, Ripple and short URL
`base62` | text <-> Base62 encoded text | `base[-_]?62(|[-_]inv(erted)?)` | 
`base63` | text <-> Base63 encoded text | `base[-_]?63(|[-_]inv(erted)?)` | 
`base69` | data <-> Base69 encoded text | `base[-_]?69` | [Base69](https://github.com/pshihn/base69) encoding (chunks of 7 bytes, 2 characters per 7 bits, `N=` for *N* padding bytes)
`base91` | text <-> Base91 encoded text | `base[-_]?91(|[-_]inv(erted)?)` | 
`base91-alt` | text <-> Alternate Base91 encoded text | `base[-_]?91[-_]alt(?:ernate)?(|[-_]inv(erted)?)` | Another version of Base91

```python
>>> codext.encode("test", "base3")
'23112113223321323322'
```

```python
>>> codecs.encode("test", "base36")
'WANEK4'
>>> codecs.decode("4WMHTK6UZL044O91NKCEB8", "base36")
'this is a test'
```

Base38 is the encoding of the payloads of the [Matter](https://github.com/project-chip/connectedhomeip) setup QR codes. The data is taken by chunks of 3 bytes, each chunk being read as a little-endian integer and written with the least significant digit first in the alphabet "`0-9A-Z-.`" (5 characters for 3 bytes, 4 for 2 bytes and 2 for 1 byte). It differs from the generic base conversion, which converts the whole input as a single integer.

```python
>>> codext.encode("Hello World!", "base38")
'KKHF3W2S013OPM3EJX11'
>>> codext.decode("KKHF3W2S013OPM3EJX11", "base38")
'Hello World!'
```

```python
>>> codext.encode("this is a test!", "base45")
'AWE+EDH44.OEOCC7WE QEX0'
>>> codext.decode('AWE+EDH44.OEOCC7WE QEX0', "base45")
'this is a test!'
```

```python
>>> codext.encode("Hello World!", "base69")
'kAZAtABBeB8A-ASB3AXBIBBBhAEAAA2='
>>> codext.decode("kAZAtABBeB8A-ASB3AXBIBBBhAEAAA2=", "base69")
'Hello World!'
```

```python
>>> codext.encode("this is a test", "base58")
'jo91waLQA1NNeBmZKUF'
>>> codext.encode("this is a test", "base58-ripple")
'jo9rA2LQwr44eBmZK7E'
>>> codext.encode("this is a test", "base58-url")
'JN91Wzkpa1nnDbLyjtf'
```

```python
>>> codecs.encode("test", "base62")
'289lyu'
>>> codecs.encode("this is a test", "base62")
'CsoB4HQ5gmgMyCenF7E'
```

```python
>>> codecs.encode("This is a test !", "base91")
'nX,<:WRT%yxth90oZB^C'
>>> codext.encode("This is a test !", "base91-alt")
'?a&[jv4S3Wg>,71@Jo#K'
```

!!! note "Generic encodings"
    
    Base encodings are available for any N other than the ones explicitely specified using the "`-generic`" suffix. Their charsets consist of printable characters from the `string` module for N up to 100 and for characters composed from the 256 possible ordinals for a greater N.

        :::python
        >>> codext.encode("test", "base3-generic")
        '12001002112210212211'
        >>> codext.encode("test", "base17-generic")
        '4cf60456'

-----

### Base85

This encoding implements various different versions of Base85.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`base85` | text <-> ascii85 | `(base[-_]?85(?:|[-_](?:adobe|x?btoa|ipv6|rfc1924|xml|z(?:eromq)?))|z85|ascii85)` | 

```python
>>> codext.encode("this is a test", "ascii85")
"FD,B0+DGm>@3BZ'F*%"
>>> codext.decode("FD,B0+DGm>@3BZ'F*%", "ascii85")
'this is a test'
>>> with open("ascii85.txt", 'w', encoding="ascii85") as f:
	f.write("this is a test")
14
>>> with open("ascii85.txt", encoding="ascii85") as f:
	f.read()
'this is a test'
```

-----

### Other base encodings

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`base100` | text <-> Base100 encoded text | `base[-_]?100|emoji` | Python 3 only
`base122` | text <-> Base122 encoded text | `base[-_]?122` | Python 3 only
`base128` | text <-> Base128 encoded text | `base[-_]?128` | Relies on the ASCII charset
`leb128` | integers <-> LEB128 (varint) bytes | `uleb128`, `varint` | unsigned integers, separated by whitespaces or commas
`sleb128` | integers <-> signed LEB128 bytes | `leb128-signed` | signed integers (two's complement)
`base1024` | data <-> Ecoji encoded text | `base[-_]?1024`, `ecoji`, `ecoji-v1`, `ecoji-v2` | 10 bits per emoji ; encodes with Ecoji version 2 by default
`bech32` | data <-> Bech32 encoded text | `bech32-<hrp>` | human-readable part required for encoding
`bech32m` | data <-> Bech32m encoded text | `bech32m-<hrp>` | human-readable part required for encoding
`base2048` | data <-> Base2048 encoded text | `base[-_]?2048` | 11 bits per character, optimised for Twitter
`base32768` | data <-> Base32768 encoded text | `base[-_]?32768` | 15 bits per character, optimised for UTF-16
`base65536` | data <-> Base65536 encoded text | `base[-_]?65536` | 16 bits per character, optimised for UTF-32

```python
>>> codecs.encode("this is a test", "base100")
'👫👟👠👪🐗👠👪🐗👘🐗👫👜👪👫'
>>> codecs.decode("👫👟👠👪🐗👠👪🐗👘🐗👫👜👪👫", "base100")
'this is a test'
```

```python
>>> codecs.encode("this is a test", "base122")
':\x1aʗ\x19\x01Rs\x10\x18$\x07#\x15ft'
>>> codecs.decode(":\x1aʗ\x19\x01Rs\x10\x18$\x07#\x15ft", "base122")
'this is a test'
```

Base2048, Base32768 and Base65536 were designed by [qntm](https://github.com/qntm/base65536). The data is written with 11, 15 or 16 bits per character, using repertoires of Unicode characters that are safe to transmit (no whitespace, no punctuation, no control or combining characters). The final bits are padded with 1s and may be written with a character of a smaller final repertoire, which can only end the encoded text. When decoding, whitespaces are ignored.

```python
>>> codext.encode("Hello, World!", "base2048")
'ԋϠɲණరϢఋԵړƶ'
>>> codext.encode("Hello, World!", "base32768")
'䩲腻㐥桥懛瀑溣'
>>> codext.encode("Hello, World!", "base65536")
'驈ꍬ慯谠𓁯饬ᔡ'
>>> codext.decode("驈ꍬ慯谠𓁯饬ᔡ", "base65536")
'Hello, World!'
```

Base1024, also known as [Ecoji](https://github.com/keith-turner/ecoji), encodes the data with 1024 emojis, that is, 10 bits per emoji. The data is taken by blocks of 5 bytes giving 4 emojis, an incomplete last block being completed with padding emojis. Ecoji has two versions with different sets of emojis: version 1 always pads the last block to 4 emojis, while version 2 (the default) only writes the first padding emoji. When decoding, both versions are supported (but cannot be mixed), whitespaces are ignored and encoded texts may be concatenated.

```python
>>> codext.encode("Hello!", "ecoji")
'🏯🔩🚗🌷🍌☕'
>>> codext.encode("Hello!", "ecoji-v1")
'🏯🔩🚗🌷🍌☕☕☕'
>>> codext.decode("🏯🔩🚗🌷🍌☕☕☕", "base1024")
'Hello!'
```

Bech32 ([BIP-173](https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki)) and Bech32m ([BIP-350](https://github.com/bitcoin/bips/blob/master/bip-0350.mediawiki)) write the data with a human-readable part (HRP), the separator "`1`", then the data regrouped by 5 bits in the alphabet "`qpzry9x8gf2tvdw0s3jn54khce6mua7l`", followed by a 6-character checksum computed over the HRP and the data. The HRP is required for encoding. When decoding, it is read from the text and only checked if given with the codec name ; the data is returned without it. The length limit of 90 characters of BIP-173 is not enforced. SegWit addresses, whose first data character is the witness version, are not decoded as such.

```python
>>> codext.encode("Hello, World!", "bech32-test")
'test1fpjkcmr09ss9wmmjd3jzzw2fmd3'
>>> codext.decode("test1fpjkcmr09ss9wmmjd3jzzw2fmd3", "bech32")
'Hello, World!'
>>> codext.encode("Hello, World!", "bech32m-test")
'test1fpjkcmr09ss9wmmjd3jzzmkehgn'
```

LEB128 (Little Endian Base 128), also known as varint, writes integers with 7 bits per byte, least significant group first, the most significant bit of each byte being set except for the last one. The signed variant (SLEB128) writes the integers in two's complement, its last byte being sign-extended. When encoding, the text holds the integers in decimal, separated by whitespaces or commas ; when decoding, the integers are separated by a space. Unlike `base128`, which converts the whole input as a single integer with the ASCII charset, these codecs work on lists of integers.

```python
>>> codext.encode("624485 300", "leb128")
'å\x8e&¬\x02'
>>> codext.decode("å\x8e&¬\x02", "varint")
'624485 300'
>>> codext.encode("-123456", "sleb128")
'À»x'
```
