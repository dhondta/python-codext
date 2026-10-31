`codext` provides a few common compression codecs.

-----

### GZip

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`gzip` | data <-> GZipped data |  | decoding tries with and without the file signature

```python
>>> codext.encode('test', "gzip")
'\x1f\x8b\x08\x00\x0esÛ_\x02ÿ+I-.\x01\x00\x0c~\x7fØ\x04\x00\x00\x00'
>>> codext.decode('\x1f\x8b\x08\x00\x0esÛ_\x02ÿ+I-.\x01\x00\x0c~\x7fØ\x04\x00\x00\x00', "gzip")
'test'
```

-----

### Huffman

[Huffman coding](https://en.wikipedia.org/wiki/Huffman_coding) gives the frequent bytes shorter codes than the rare ones, with an optimal prefix code. This codec writes the code as a [canonical Huffman code](https://en.wikipedia.org/wiki/Canonical_Huffman_code) (given by the lengths of the codes only), in a self-describing format: the number of distinct bytes minus 1 (1 byte), each byte with the length of its code (2 bytes each), the number of padding bits at the end (1 byte), then the codes of the bytes of the text, from the most significant bit.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`huffman` | data <-> Huffman-coded data |  | malformed data replaced, dropped or left with a non-strict errors handling ; as the length of the text is not stored, data truncated at the end of a code gives a truncated text

```python
>>> codext.encode(b"abracadabra", "huffman")
b'\x04a\x01b\x03c\x03d\x03r\x03\x01N\xac\x9c'
>>> codext.decode(b"\x04a\x01b\x03c\x03d\x03r\x03\x01N\xac\x9c", "huffman")
b'abracadabra'
```

-----

### Lempel-Ziv

This implements the algorithm of Lempel and Ziv of 1977 and 1978.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`lz77` | data <-> LZ77-compressed data | | 
`lz78` | data <-> LZ78-compressed data | | 

```python
>>> codecs.encode("A test string !", "lz77")
' \x88\x0e\x86S\x99ÐA\x0029\x1aMÆq\x00\x84'
>>> codecs.decode(" \x88\x0e\x86S\x99ÐA\x0029\x1aMÆq\x00\x84", "lz77")
'A test string !'
```

```python
>>> codext.encode("A test string !", "lz78")
'A\x00 \x00t\x00e\x00s\x03 \x05t\x00r\x00i\x00n\x00g\x02!'
>>> codext.decode("A\x00 \x00t\x00e\x00s\x03 \x05t\x00r\x00i\x00n\x00g\x02!", "lz78")
'A test string !'
```

-----

### PKZip

This implements multiple compression types available in the native [`zipfile`](https://docs.python.org/3/library/zipfile.html) library.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`pkzip_deflate` | data <-> Deflated data | `deflate`, `zip_deflate` | Python3 only
`pkzip_bzip2` | data <-> Bzipped data | `bz2`, `bzip2`, `zip_bz2` | Python3 only
`pkzip_lzma` | data <-> LZMA-compressed data | `lzma`, `zip_lzma` | Python3 only

```python
>>> codecs.encode("a test string", "deflate")
'KT(I-.Q(.)ÊÌK\x07\x00'
>>> codecs.decode("KT(I-.Q(.)ÊÌK\x07\x00", "zip_deflate")
'a test string'
```

```python
>>> codecs.encode("a test string", "bzip2")
'BZh91AY&SY°\x92µÏ\x00\x00\x01\x11\x80@\x00"¡\x1c\x00 \x00"\x1a\x07¤ É\x88u\x95Á`Òñw$S\x85\t\x0b\t+\\ð'
>>> codecs.decode("BZh91AY&SY°\x92µÏ\x00\x00\x01\x11\x80@\x00\"¡\x1c\x00 \x00\"\x1a\x07¤ É\x88u\x95Á`Òñw$S\x85\t\x0b\t+\\ð", "bz2")
'a test string'
```

```python
>>> codecs.encode("a test string", "lzma")
'\t\x04\x05\x00]\x00\x00\x80\x00\x000\x88\n\x86\x94\\Uf\x14Þ\x82*\x11ëê\x93fÿý\x84 \x00'
>>> codecs.decode("\t\x04\x05\x00]\x00\x00\x80\x00\x000\x88\n\x86\x94\\Uf\x14Þ\x82*\x11ëê\x93fÿý\x84 \x00", "zip_lzma")
'a test string'
```

-----

### Run-Length Encoding

This replaces each run of identical consecutive characters by its length followed by the character. The default variant writes the length in decimal ; it cannot encode digits, as they would be confused with the lengths. The `compact` variant omits a length of 1, the `suffix` variant writes the length after the character (both can be combined as `rle-compact-suffix`), while the `bytes` variant writes the length as a single character (code point 1 to 255) and can encode any input. The `escape` variant keeps single characters as they are and writes a run as the character twice followed by the number of extra repeats as a single character (code point 0 to 255) ; it can encode any input and does not expand text without repeats.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`rle` | text <-> RLE-compressed text | `run-length`, `runlength`, `run_length_encoding` | digits cannot be encoded ; decoding accepts lengths of 1 being omitted
`rle-compact` | text <-> RLE-compressed text | `run-length-compact` | lengths of 1 are omitted
`rle-suffix` | text <-> RLE-compressed text | `run-length-suffix` | lengths after the characters (e.g. `A3B2`)
`rle-compact-suffix` | text <-> RLE-compressed text | `run-length-compact-suffix` | lengths after the characters, lengths of 1 being omitted
`rle-bytes` | data <-> RLE-compressed data | `run-length-bytes` | each run as a (length, character) pair, longer runs being split
`rle-escape` | data <-> RLE-compressed data | `run-length-escape` | runs as a repeated character and a count of extra repeats, longer runs being split

```python
>>> codext.encode("WWWWWWWWWWWWBWWWWWWWWWWWWBBB", "rle")
'12W1B12W3B'
>>> codext.encode("WWWWWWWWWWWWBWWWWWWWWWWWWBBB", "rle-compact")
'12WB12W3B'
>>> codext.decode("12WB12W3B", "run-length")
'WWWWWWWWWWWWBWWWWWWWWWWWWBBB'
>>> codext.encode("WWWWWWWWWWWWBWWWWWWWWWWWWBBB", "rle-suffix")
'W12B1W12B3'
>>> codext.encode("WWWWWWWWWWWWBWWWWWWWWWWWWBBB", "rle-compact-suffix")
'W12BW12B3'
>>> codext.encode("AAAB", "rle-bytes")
'\x03A\x01B'
>>> codext.encode("AAAAAB", "rle-escape")
'AA\x03B'
>>> codext.decode("AA\x03B", "rle-escape")
'AAAAAB'
```

-----

### Zstandard

[Zstandard](https://datatracker.ietf.org/doc/html/rfc8878) (zstd) combines LZ77-style matching with entropy coding, in frames starting with a magic number. This codec relies on the `compression.zstd` module of the standard library (Python 3.14 and later) or on its backport, the [`backports.zstd`](https://pypi.org/project/backports.zstd/) package, installed as a dependency for the previous versions of Python ; it is not available without them.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`zstd` | data <-> Zstandard-compressed data | `zstandard`, `zstd-1`, `zstd_19`, ... | parametrized with the compression level, from 1 to 22 (default: 3) ; decoding handles concatenated frames

```python
>>> data = codext.encode(b"This is a test " * 10, "zstd-19")
>>> data[:4]
b'(\xb5/\xfd'
>>> codext.decode(data, "zstd")
b'This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test '
```
