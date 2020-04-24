With `codext`, the `codecs` library has multiple new encodings in addition to [the native ones](https://docs.python.org/3.8/library/codecs.html#standard-encodings), like presented hereafter.

Unless explicitely specified, each codec supports writing to and reading from a file.

-----

### Ascii85

This encoding relies on the `base64` library and is only supported in Python 3.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`ascii85` | Ascii85 <-> text | none | Python 3 only

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

### Baconian Cipher

It support only letters.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`bacon` | Bacon <-> text | `bacon-cipher`, `baconian_cipher`, `bacon-01` | Dynamic tokens mapping ; we can define a mapping of encoding's tokens (original tokens: `ab`)

```python
>>> codext.encode("this is a test", "bacon")
'baaba aabbb abaaa baaab  abaaa baaab  aaaaa  baaba aabaa baaab baaba'
>>> codext.encode("this is a test", "bacon_01")
'10010 00111 01000 10001  01000 10001  00000  10010 00100 10001 10010'
>>> codext.decode("-..-. ..--- .-... -...-  .-... -...-  .....  -..-. ..-.. -...- -..-.", "bacon_.-")
'THIS IS A TEST'
```

-----

### Braille

It supports letters, digits and some special characters.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`braille` | Braille <-> text | none | Python 3 only

```python
>>> codext.encode("this is a test", "braille")
'⠞⠓⠊⠎⠀⠊⠎⠀⠁⠀⠞⠑⠎⠞'
>>> codext.encode("THIS IS A TEST", "braille")
'⠞⠓⠊⠎⠀⠊⠎⠀⠁⠀⠞⠑⠎⠞'
>>> codext.decode("⠞⠓⠊⠎⠀⠊⠎⠀⠁⠀⠞⠑⠎⠞", "braille")
'this is a test'
```

-----

### DNA

This implements the 8 methods of ATGC nucleotides following the rule of complementary pairing, according the literature about coding and computing of DNA sequences.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`dna` (rule 1) | DNA-1 <-> text | `dna1`, `dna-1`, `dna_1` | 
`dna` (rule X) | DNA-X <-> text | ... | 
`dna` (rule 8) | DNA-8 <-> text | `dna8`, `dna-8`, `dna_8` | 

```python
>>> for i in range(8):
        print(codext.encode("this is a test", "dna-%d" % (i + 1)))
GTGAGCCAGCCGGTATACAAGCCGGTATACAAGCAGACAAGTGAGCGGGTATGTGA
CTCACGGACGGCCTATAGAACGGCCTATAGAACGACAGAACTCACGCCCTATCTCA
ACAGATTGATTAACGCGTGGATTAACGCGTGGATGAGTGGACAGATAAACGCACAG
AGACATTCATTAAGCGCTCCATTAAGCGCTCCATCACTCCAGACATAAAGCGAGAC
TCTGTAAGTAATTCGCGAGGTAATTCGCGAGGTAGTGAGGTCTGTATTTCGCTCTG
TGTCTAACTAATTGCGCACCTAATTGCGCACCTACTCACCTGTCTATTTGCGTGTC
GAGTGCCTGCCGGATATCTTGCCGGATATCTTGCTGTCTTGAGTGCGGGATAGAGT
CACTCGGTCGGCCATATGTTCGGCCATATGTTCGTCTGTTCACTCGCCCATACACT
>>> codext.decode("GTGAGCCAGCCGGTATACAAGCCGGTATACAAGCAGACAAGTGAGCGGGTATGTGA", "dna-1")
'this is a test'
```

-----

### Leetspeak

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`leetspeak` | LeetSpeak <-> text | `leet`, `1337`, `leetspeak` | based on minimalistic elite speaking rules

```python
>>> codext.encode("this is a test", "leetspeak")
'7h15 15 4 7357'
>>> codext.decode("7h15 15 4 7357", "leetspeak")
'ThIS IS A TEST'
```

!!! warning "Lossy conversion"
    
    This "encoding" is lossy, as it can be seen in the previous example.

-----

### Markdown

This is only for "encoding" (converting) Markdown to HTML.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`markdown` | Markdown --> HTML | `markdown`, `Markdown`, `md` | unidirectional !

```python
>>> codext.encode("# Test\nparagraph", "markdown")
'<h1>Test</h1>\n\n<p>paragraph</p>\n'
```

-----

### Morse

It supports of course letters and digits, but also a few special characters: `.,;:?!/\\@&=-_'" $()`.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`morse` | Morse <-> text | none | uses whitespace as a separator, dynamic tokens mapping ; we can define a mapping of encoding's tokens (original tokens: `/-.`)

```python
>>> codext.encode("this is a test", "morse")
'- .... .. ... / .. ... / .- / - . ... -'
>>> codext.encode("this is a test", "morse/-.")
'- .... .. ... / .. ... / .- / - . ... -'
>>> codext.encode("this is a test", "morse_ABC")
'B CCCC CC CCC A CC CCC A CB A B C CCC B'
>>> codext.decode("- .... .. ... / .. ... / .- / - . ... -", "morse")
'this is a test'
>>> with codext.open("morse.txt", 'w', encoding="morse") as f:
	f.write("this is a test")
14
>>> with codext.open("morse.txt", encoding="morse") as f:
	f.read()
'this is a test'
```

-----

### Nokia

At this time, only Nokia 3310 keystrokes is supported.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`nokia3310` | Nokia 3310 keystrokes <-> text | `nokia-3310`, `nokia_3310` | uses "`-`" as a separator for encoding, "`-`" or "`_`" or whitespace for decoding

```python
>>> codext.encode("this is a test", "nokia3310")
'8-44-444-7777-0-444-7777-0-2-0-8-33-7777-8'
>>> codext.decode("8_44_444_7777_0_444_7777_0_2_0_8_33_7777_8", "nokia3310")
'this is a test'
>>> codext.decode("8_44_444_7777_0-444-7777_0-2_0_8_33-7777-8", "nokia3310")
'this is a test'
```

-----

### ROT N

This is a dynamic encoding, that is, it can be called with an integer to define the ROT offset. Encoding will apply a positive offset, decoding will apply a negative one.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`rotN` | ROT(1) <-> text | `rot1`, `rot-1`, `rot_1` | 
`rotN` | ROT(X) <-> text | ... | 
`rotN` | ROT(25) <-> text | `rot25`, `rot-25`, `rot_25` | 

```python
>>> codext.encode("this is a test", "rot-15")
'iwxh xh p ithi'
>>> codext.encode("iwxh xh p ithi", "rot20")
'cqrb rb j cnbc'
>>> codext.decode("cqrb rb j cnbc", "rot_9")
'this is a test'
```

-----

### XOR with 1 byte

This is a dynamic encoding, that is, it can be called with an integer to define the ordinal of the byte to XOR with the input text.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`xorN` | XOR(1) <-> text | `XOR1`, `xor1`, `xor-1`, `xor_1` | 
`xorN` | XOR(X) <-> text | ... | 
`xorN` | XOR(255) <-> text | `XOR255`, `xor255`, `xor-255`, `xor_255` | 

```python
>>> codext.encode("this is a test", "xor-10")
'~bcy*cy*k*~oy~'
>>> codext.encode("this is a test", "xor-30")
'jvwm>wm>\x7f>j{mj'
>>> codext.decode("this is a test", "xor-30")
'jvwm>wm>\x7f>j{mj'
>>> codext.encode("~bcy*cy*k*~oy~", "xor-10")
'this is a test'
```

-----

### Whitespaces

This simple encoding replaces zeros and ones of the binary version of the input text with spaces and tabs. It is supported either with its original mapping or with the inverted mapping.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`whitespace` | Whitespaces <-> text | `whitespaces?-inv(erted)?` | The default encoding uses tabs for zeros and spaces for ones

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
