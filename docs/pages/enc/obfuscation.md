`codext` implements some obfuscation encodings, i.e. encodings that are presented as encryption (by online JavaScript encryption tools or to store passwords in configuration files) but that use no key: anyone who knows the algorithm can decode them. The encodings that really have a key are listed in [Ciphers](ciphers.md).

-----

### ARABICA-2RS

This toy encoding comes from online JavaScript encryption tools. The text is encoded like JavaScript's `encodeURIComponent()` does (e.g. a whitespace becomes `%20`), then each of its characters is substituted by an Arabic letter (or a similar character), the encoded text ending with `ش`. The original JavaScript inserts random spaces, which are ignored when decoding ; this codec gives an encoded text without spaces.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`arabica-2rs` | text <-> ARABICA-2RS encoded text | `arabica2rs`, `arabica_2rs` | the left-to-right marks around `ݣ` are optional when decoding

```python
>>> codext.encode("this is a test", "arabica-2rs")
'حرقطﺿأﺹقطﺿأﺹغﺿأﺹحبطحش'
>>> codext.decode("حرقطﺿأﺹقطﺿأﺹغﺿأﺹحبطحش", "arabica2rs")
'this is a test'
```

-----

### ATOM-128

This toy encoding comes from online JavaScript encryption tools. It is Base64 with a shuffled alphabet, whose 65th character (`C`) is used for padding. As in the original JavaScript, the text is first escaped with JavaScript's `escape()` (e.g. a whitespace becomes `%20`), and unescaped after decoding.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`atom128` | text <-> ATOM-128 encoded text | `atom-128`, `atom_128` | 

```python
>>> codext.encode("this is a test", "atom128")
'0IXBnsgsSI6tQfPqKDgsSoA6nmbC'
>>> codext.decode("0IXBnsgsSI6tQfPqKDgsSoA6nmbC", "atom-128")
'this is a test'
```

-----

### CHINZO-72C

This toy encoding comes from online JavaScript encryption tools. The pairs of letters `oo`, `ii`, `ee`, `tt` and `rr` are first replaced by Chinese characters, then the text is encoded like JavaScript's `encodeURIComponent()` does and each of its characters is substituted by a Chinese character followed by a space, the encoded text ending with `吴`.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`chinzo-72c` | text <-> CHINZO-72C encoded text | `chinzo72c`, `chinzo_72c` | spaces ignored when decoding

!!! warning "Pairs of letters"

    As decoding gives back the pairs of letters, a text holding one of the 5 Chinese characters replacing them (`讲`, `邻`, `头`, `会` and `歷`) is not decoded as it was.

```python
>>> codext.encode("this is a test", "chinzo-72c")
'岛 拉 玛 夫 题 防 呒 玛 夫 题 防 呒 法 题 防 呒 岛 伐 夫 岛 吴'
>>> codext.decode("岛 拉 玛 夫 题 防 呒 玛 夫 题 防 呒 法 题 防 呒 岛 伐 夫 岛 吴", "chinzo72c")
'this is a test'
```

-----

### Cisco Type 7

This implements the reversible Cisco IOS type 7 password encoding: each byte is XORed with a fixed key, starting at an offset given by the salt (from 0 to 15), and the result is the salt as two decimal digits followed by the XORed bytes in hexadecimal. Decoding reads the salt from the input.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`cisco-type7` | text <-> Cisco type 7 encoded text | `cisco7`, `type7`, `cisco_type_7`, ... | parameterized with the salt used for encoding, e.g. `cisco-type7-8` (default: 0)

```python
>>> codext.encode("this is a test", "cisco-type7-8")
'083544471A590C04520A4C102F3830'
>>> codext.decode("0822455D0A16", "cisco-type7")
'cisco'
```

-----

### Citrix CTX1

This implements the Citrix CTX1 password encoding algorithm.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`citrix` | text <-> Citrix CTX1 encoded text | `citrix`, `citrix-1`, `citrix_ctx1` | 

```python
>>> codext.encode("this is a test", "citrix-ctx1")
'NBBMNAAGIDEPJJBMNIFNIMEMJKEL'
>>> codext.decode("NBBMNAAGIDEPJJBMNIFNIMEMJKEL", "citrix-ctx1")
'this is a test'
```

-----

### ESAB-46

This toy encoding ("Base-64" reversed) comes from online JavaScript encryption tools. Like [ATOM-128](#atom-128), it is Base64 with a shuffled alphabet, whose 65th character (`/`) is used for padding, and the text is first escaped with JavaScript's `escape()`, then unescaped after decoding.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`esab46` | text <-> ESAB-46 encoded text | `esab-46`, `esb46`, `esb_46` | 

```python
>>> codext.encode("this is a test", "esab46")
'9sRZ8i0ivsVj6z5gLy0iv4xV8nw/'
>>> codext.decode("9sRZ8i0ivsVj6z5gLy0iv4xV8nw/", "esab-46")
'this is a test'
```

-----

### FERON-74

This toy encoding comes from online JavaScript encryption tools. Like [ATOM-128](#atom-128), it is Base64 with a shuffled alphabet, whose 65th character (`4`) is used for padding, and the text is first escaped with JavaScript's `escape()`, then unescaped after decoding.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`feron74` | text <-> FERON-74 encoded text | `feron-74`, `feron_74` | 

```python
>>> codext.encode("this is a test", "feron74")
'sbxMC161WbyZ/rSiNq61WcDyCnA4'
>>> codext.decode("sbxMC161WbyZ/rSiNq61WcDyCnA4", "feron-74")
'this is a test'
```

-----

### GILA7

This toy encoding comes from online JavaScript encryption tools. Like [ATOM-128](#atom-128), it is Base64 with a shuffled alphabet, whose 65th character (`G`) is used for padding, and the text is first escaped with JavaScript's `escape()`, then unescaped after decoding.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`gila7` | text <-> GILA7 encoded text | `gila-7`, `gila_7` | 

```python
>>> codext.encode("this is a test", "gila7")
'3+1QqbzbB+Odcg=5v0zbBWfOqxyG'
>>> codext.decode("3+1QqbzbB+Odcg=5v0zbBWfOqxyG", "gila-7")
'this is a test'
```

-----

### HAZZ-15

This toy encoding comes from online JavaScript encryption tools. It is Base64 with a shuffled alphabet, whose 65th character (`5`) is used for padding. As in the original JavaScript, the text is first escaped with JavaScript's `escape()` (e.g. a whitespace becomes `%20`), and unescaped after decoding ; encoded texts made from the UTF-8 bytes of the text (without escaping) are decoded as well.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`hazz15` | text <-> HAZZ-15 encoded text | `hazz-15`, `hazz_15` | 

```python
>>> codext.encode("this is a test", "hazz15")
'3m7Vqbzb+mFdjgiGv0zb+6fFq=y5'
>>> codext.decode("3m7Vqbzb+mFdjgiGv0zb+6fFq=y5", "hazz-15")
'this is a test'
```

-----

### HINDIA-4X

This toy encoding comes from online JavaScript encryption tools. The pairs of letters `oo`, `ii`, `ee`, `tt` and `rr` are first replaced by other characters, then the text is encoded like JavaScript's `encodeURIComponent()` does and its characters, in reverse order, are each substituted by a Bengali or Devanagari character, a space being inserted every 4 characters and the encoded text ending with `ভ`.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`hindia-4x` | text <-> HINDIA-4X encoded text | `hindia4x`, `hindia_4x` | spaces ignored when decoding

!!! warning "Pairs of letters"

    As decoding gives back the pairs of letters, a text holding one of the 5 characters replacing them (`ṍ`, `¡`, `ə`, `ṯ` and `ṝ`) is not decoded as it was.

```python
>>> codext.encode("this is a test", "hindia-4x")
'ছএकছ उचवफ उचवএ চउचव এচশছভ'
>>> codext.decode("ছএकছ उचवफ उचवএ চउचव এচশছভ", "hindia4x")
'this is a test'
```

-----

### JAPOO-C2S

This toy encoding comes from online JavaScript encryption tools. The text is encoded like JavaScript's `encodeURIComponent()` does, then each of its characters is substituted by a Chinese or Japanese character followed by a space, some pairs of identical characters (e.g. `貴 貴 `) being then replaced by another character (e.g. `詞 `), and the encoded text ends with `类`.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`japoo-c2s` | text <-> JAPOO-C2S encoded text | `japooc2s`, `japoo_c2s` | spaces ignored when decoding

```python
>>> codext.encode("this is a test", "japoo-c2s")
'徒 卵 語 簡 場 誰 貴 語 簡 場 誰 貴 是 場 誰 貴 徒 或 簡 徒 类'
>>> codext.decode("徒 卵 語 簡 場 誰 貴 語 簡 場 誰 貴 是 場 誰 貴 徒 或 簡 徒 类", "japooc2s")
'this is a test'
```

-----

### KOREX-3S

This toy encoding comes from online JavaScript encryption tools. The text is encoded like JavaScript's `encodeURIComponent()` does and its characters, in reverse order, are each substituted by a Korean Hangul syllable (or a Chinese character) followed by a space, the encoded text ending with `한`.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`korex-3s` | text <-> KOREX-3S encoded text | `korex3s`, `korex_3s` | spaces ignored when decoding

```python
>>> codext.encode("this is a test", "korex-3s")
'지 등 대 지 고 이 南 국 고 이 南 등 주 고 이 南 등 주 선 지 한'
>>> codext.decode("지 등 대 지 고 이 南 국 고 이 南 등 주 고 이 南 등 주 선 지 한", "korex3s")
'this is a test'
```

-----

### MEGAN-35

This toy encoding comes from online JavaScript encryption tools. It is Base64 with a shuffled alphabet, whose 65th character (`5`) is used for padding. As in the original JavaScript, the text is first escaped with JavaScript's `escape()` (e.g. a whitespace becomes `%20`), and unescaped after decoding ; encoded texts made from the UTF-8 bytes of the text (without escaping) are decoded as well.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`megan35` | text <-> MEGAN-35 encoded text | `megan-35`, `megan_35` | 

```python
>>> codext.encode("this is a test", "megan35")
'nLX0msesRL1tOdNqicesRM=1mxb5'
>>> codext.decode("nLX0msesRL1tOdNqicesRM=1mxb5", "megan-35")
'this is a test'
```

-----

### TIGO-3FX

This toy encoding comes from online JavaScript encryption tools. It is Base64 with a shuffled alphabet, whose 65th character (`X`) is used for padding. As in the original JavaScript, the text is first escaped with JavaScript's `escape()` (e.g. a whitespace becomes `%20`), and unescaped after decoding ; encoded texts made from the UTF-8 bytes of the text (without escaping) are decoded as well.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`tigo-3fx` | text <-> TIGO-3FX encoded text | `tigo3fx`, `tigo_3fx` | 

```python
>>> codext.encode("this is a test", "tigo-3fx")
'BAYhcO+OwAf3t1VMm/+Ow8ZfcRWX'
>>> codext.decode("BAYhcO+OwAf3t1VMm/+Ow8ZfcRWX", "tigo3fx")
'this is a test'
```

-----

### TRIPO-5

This toy encoding comes from online JavaScript encryption tools. It is Base64 with a shuffled alphabet, whose 65th character (`T`) is used for padding. As in the original JavaScript, the text is first escaped with JavaScript's `escape()` (e.g. a whitespace becomes `%20`), and unescaped after decoding ; encoded texts made from the UTF-8 bytes of the text (without escaping) are decoded as well.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`tripo-5` | text <-> TRIPO-5 encoded text | `tripo5`, `tripo_5` | 

```python
>>> codext.encode("this is a test", "tripo-5")
'dEBqW2=2mE5K7YGwSX=2m+R5W0QT'
>>> codext.decode("dEBqW2=2mE5K7YGwSX=2m+R5W0QT", "tripo5")
'this is a test'
```

-----

### ZONG22

This toy encoding comes from online JavaScript encryption tools. It is Base64 with a shuffled alphabet, whose 65th character (`2`) is used for padding. As in the original JavaScript, the text is first escaped with JavaScript's `escape()` (e.g. a whitespace becomes `%20`), and unescaped after decoding ; encoded texts made from the UTF-8 bytes of the text (without escaping) are decoded as well.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`zong22` | text <-> ZONG22 encoded text | `zong-22`, `zong_22` | 

```python
>>> codext.encode("this is a test", "zong22")
'PyglpexeXyNFwd0QIbxeXfYNpz52'
>>> codext.decode("PyglpexeXyNFwd0QIbxeXfYNpz52", "zong-22")
'this is a test'
```
