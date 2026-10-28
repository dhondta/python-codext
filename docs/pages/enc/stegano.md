`codext` defines a few steganography-related encodings. While encoding is not really steganography (that is, concealing data within data), the following codecs are worth creating this category as they relate to converting data into something that could mislead the unaware reader.

-----

### Hexagrams (I Ching)

This uses Base64 and then encodes output characters to [I Ching Hexagrams](https://en.wikipedia.org/wiki/Hexagram_%28I_Ching%29) such that implemented [here](https://github.com/qntm/hexagram-encode).

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`hexagram` | text <-> hexagrams-encoded Base64 | `hexagrams`, `i-ching-hexagrams`, `iching` | Python3 only

```python
>>> codext.encode("this is a test", "hexagram")
'䷰䷭䷚䷔䷞䷺䷗䷔䷞䷺䷗䷚䷏䷊䷂䷕䷞䷈䷇☯'
>>> codext.decode("䷰䷭䷚䷔䷞䷺䷗䷔䷞䷺䷗䷚䷏䷊䷂䷕䷞䷈䷇☯", "iching")
'this is a test'
```

-----

### Klopf Code

This is a Polybius code with the trivial alphabetical distribution ("A" -> (1,1), "B" -> (2,1), ...). This can be tested [here](https://gc.de/gc/klopfcode/).

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`klopf` | text <-> klopf encoded text | `klopfcode` | 

```python
>>> codext.encode("this is a test", "klopf")
'44324234 4234 11 44513444'
>>> codext.decode("44324234 4234 11 44513444", "klopf")
'THIS IS A TEST'
```

-----

### Resistor Color Codes

This uses the [electronic color code](https://en.wikipedia.org/wiki/Electronic_color_code#Resistor_color-coding) to encode digits, displaying colors in the terminal with ANSI color codes.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`resistor` | text <-> resistor colors | `condensator`, `resistors-color`, `resistor_color_code` | visually, it only works in a terminal supporting ANSI color codes

```python
>>> codext.encode("1234", "resistor")
'\x1b[48;5;130m \x1b[0;00m\x1b[48;5;1m \x1b[0;00m\x1b[48;5;214m \x1b[0;00m\x1b[48;5;11m \x1b[0;00m'
>>> codext.decode("\x1b[48;5;130m \x1b[0;00m\x1b[48;5;1m \x1b[0;00m\x1b[48;5;214m \x1b[0;00m\x1b[48;5;11m \x1b[0;00m", "condensators_color")
'1234'
```

-----

### Rick Cipher

This converts letters to words from Rick Astley's famous song "*Never gonna give you up*".

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`rick` | text <-> words from Risk's song | `rick-astley`, `rick_cipher`, `rick-astley-cipher` | case-insensitive while encoding

```python
>>> codext.encode("Test String", "rick")
'TELL UP gonna TELL + gonna TELL NEVer You AROUND Gonna'
>>> codext.decode("TELL UP gonna TELL + gonna TELL NEVer You AROUND Gonna", "rick")
'TEST STRING'
```

-----

### SMS (T9)

This codec implements the SMS encoding, also caled T9, that is the conversion from characters to their corresponding phone keystrokes.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`sms` | text <-> phone keystrokes | `nokia`, `nokia_3310`, `t9` | uses "`-`" as a separator for encoding, "`-`" or "`_`" or whitespace for decoding

```python
>>> codext.encode("this is a test", "sms")
'8-44-444-7777-0-444-7777-0-2-0-8-33-7777-8'
>>> codext.decode("8_44_444_7777_0_444_7777_0_2_0_8_33_7777_8", "nokia")
'this is a test'
>>> codext.decode("8_44_444_7777_0-444-7777_0-2_0_8_33-7777-8", "t9")
'this is a test'
```

-----

### Unicode Tags

This codec hides ASCII text in the invisible characters of the [Unicode Tags block](https://www.unicode.org/charts/PDF/UE0000.pdf) (`U+E0000` to `U+E007F`), each character being shifted by `0xE0000`. This technique, also called *ASCII smuggling*, is used to [hide instructions in the input of language models](https://embracethered.com/blog/posts/2024/hiding-and-finding-text-with-unicode-tags/). When decoding, every character out of the Tags block is ignored, so the hidden text can be extracted from its cover text directly.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`unicode-tags` | ASCII text <-> Unicode tag characters | `unicode_tag`, `unicodetags`, `tags`, `tag-smuggling` | ASCII only (non-ASCII characters are encoding errors ; with `errors="replace"`, the replacement character is a hidden `?`)
`unicode-tags-wrapped` | ASCII text <-> Unicode tag characters | `tags-wrapped`, `tag-smuggling-wrapped` | surrounds the hidden text with the BEGIN tag (`U+E0001`) and the CANCEL \U000e00 (`U+E007F`), which are stripped when decoding

```python
>>> codext.encode("Hi!", "unicode-tags")
'\U000e0048\U000e0069\U000e0021'
>>> stego = "Please summarize " + codext.encode("ignore previous instructions", "unicode-tags") + "this."
>>> print(stego)
Please summarize this.
>>> codext.decode(stego, "unicode-tags")
'ignore previous instructions'
>>> codext.decode(codext.encode("Hi", "unicode-tags-wrapped"), "unicode-tags-wrapped")
'Hi'
```

-----

### Whitespaces

This simple encoding replaces zeros and ones of the binary version of the input text with spaces and tabs. It is supported either with its original mapping or with the inverted mapping.

!!! warning "Encoding, not programming !"
    
    This should not be confused with the [whitespace esoteric language](https://en.wikipedia.org/wiki/Whitespace_(programming_language)).

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`whitespace` | text <-> whitespaces and tabs | `whitespaces?-inv(erted)?` | The default encoding uses tabs for zeros and spaces for ones
`whitespace_after_before` | text <-> whitespaces[letter]whitespaces | | This codec encodes characters as new characters with whitespaces before and after according to an equation described in the codec name (e.g. "`whitespace+2*after-3*before`") ; characters that no number of whitespaces (0 to 20) can shift to a printable one (e.g. whitespaces, control or most non-ASCII characters) cannot be encoded

```python
>>> codext.encode("test", "whitespace")
'\t   \t \t\t\t  \t\t \t \t   \t\t  \t   \t \t\t'
>>> codext.encode("test", "whitespaces")
'\t   \t \t\t\t  \t\t \t \t   \t\t  \t   \t \t\t'
>>> codext.encode("test", "whitespaces-inv")
' \t\t\t \t   \t\t  \t \t \t\t\t  \t\t \t\t\t \t  '
>>> codext.decode(" \t\t\t \t   \t\t  \t \t \t\t\t  \t\t \t\t\t \t  ", "whitespaces_inverted")
'test'
```

```python
>>> codext.encode("test", "whitespace+after-before")
'             m      \n        l               \n   u     \n            m     '
>>> codext.decode("             m      \n        l               \n   u     \n            m     ", "whitespace+after-before")
'test'
```

-----

### Zero-Width Characters

This codec hides text in invisible Unicode characters. The result can be inserted anywhere in a cover text: when decoding, every character that is not part of the codec's alphabet is ignored, so the cover text does not need to be removed first.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`zero-width` | text <-> zero-width characters | `zerowidth`, `zero_width`, `zero-width-binary`, `zero-width-2` | bits of the UTF-8 bytes ; `U+200B` (zero-width space) for 0, `U+200C` (zero-width non-joiner) for 1
`zero-width-ternary` | text <-> zero-width characters | `zero-width-zwsp`, `zero-width-3` | 11 base-3 digits per character with `U+200B`, `U+200C`, `U+200D` ; compatible with the `MODE_ZWSP` of [zwsp-steg](https://github.com/enodari/zwsp-steg-py) ; code points up to `U+2B3FA`
`zero-width-quinary` | text <-> zero-width characters | `zero-width-full`, `zero-width-5` | 7 base-5 digits per character with `U+200B` to `U+200F` ; compatible with the `MODE_FULL` of [zwsp-steg](https://github.com/enodari/zwsp-steg-py) ; code points up to `U+1312C` (no emoji)

```python
>>> codext.encode("A", "zero-width")
'\u200b\u200c\u200b\u200b\u200b\u200b\u200b\u200c'
>>> cover = "Nothing to see here."
>>> stego = cover[:8] + codext.encode("secret", "zero-width") + cover[8:]
>>> print(stego)
Nothing to see here.
>>> len(cover), len(stego)
(20, 68)
>>> codext.decode(stego, "zero-width")
'secret'
>>> codext.decode(codext.encode("secret", "zero-width-full"), "zero-width-quinary")
'secret'
```
