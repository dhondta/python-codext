### Classical base 2^N encodings

This namely adds the classical BaseXX encodings like 16 (hexadecimal) and 32 (RFC 3548), which are not available in the native codecs.

Common base encodings with N a power of 2:

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`base2` | Base2 <-> text | `(base[-_]?2|bin)-inv(erted)?` | 
`base4` | Base4 <-> text | `base[-_]?4-inv(erted)` | charset: `1234`
`base8` | Base8 <-> text | `base[-_]?8-inv(erted)` | charset: `abcdefgh`
`base16` | Base16 <-> text | `base[-_]?16-inv(erted)` | 
`base32` | Base32 <-> text | `base[-_]?32-inv(erted)` | 
`zbase32` | ZBase32 <-> text | `z[-_]?base[-_]?32` | human-oriented Base32
`base64` | Base64 <-> text | `base[-_]?64-inv(erted)` | 

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
`base3` | Base3 <-> text | `base[-_]?36(|[-_]inv(erted)?)` | 
`base36` | Base36 <-> text | `base[-_]?36(|[-_]inv(erted)?)` | 
`base58` | Base58 <-> text | `base[-_]?58(|[-_](bc|bitcoin|rp|ripple|fl|flickr|short[-]?url|url))` | supports Bitcoin, Ripple and short URL
`base62` | Base62 <-> text | `base[-_]?62(|[-_]inv(erted)?)` | 

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

!!! note "Generic encodings"
    
    Base encodings are available for any N other than the ones explicitely specified using the "`-generic`" suffix. Their charsets consist of printable characters from the `string` module for N up to 100 and for characters composed from the 256 possible ordinals for a greater N.

        :::python
        >>> codext.encode("test", "base3-generic")
        '12001002112210212211'
        >>> codext.encode("test", "base17-generic")
        '4cf60456'

-----

### Other base encodings

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`base85` | Base85 <-> text | `base[-_]?85` | Python 3 only (relies on `base64` module)
`base100` | Base100 <-> text | `base[-_]?100|emoji` | Python 3 only

With Python 3, `base85` and `base100` (emoji's) are also supported.

```python
>>> codecs.encode("this is a test", "base85")
'bZBXFAZc?TVIXv6b94'
>>> codecs.decode("bZBXFAZc?TVIXv6b94", "base85")
'this is a test'
```

```python
>>> codecs.encode("this is a test", "base100")
'👫👟👠👪🐗👠👪🐗👘🐗👫👜👪👫'
>>> codecs.decode("👫👟👠👪🐗👠👪🐗👘🐗👫👜👪👫", "base100")
'this is a test'
```
