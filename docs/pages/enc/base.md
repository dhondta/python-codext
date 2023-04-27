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
`base45` | text <-> Base45 encoded text | `base[-_]?45(|[-_]inv(erted)?)` | 
`base58` | text <-> Base58 encoded text | `base[-_]?58(|[-_](bc|bitcoin|rp|ripple|fl|flickr|short[-]?url|url))` | Supports Bitcoin, Ripple and short URL
`base62` | text <-> Base62 encoded text | `base[-_]?62(|[-_]inv(erted)?)` | 
`base63` | text <-> Base63 encoded text | `base[-_]?63(|[-_]inv(erted)?)` | 
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

```python
>>> codext.encode("this is a test!", "base45")
'AWE+EDH44.OEOCC7WE QEX0'
>>> codext.decode('AWE+EDH44.OEOCC7WE QEX0', "base45")
'this is a test!'
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

