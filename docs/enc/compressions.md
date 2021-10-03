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

