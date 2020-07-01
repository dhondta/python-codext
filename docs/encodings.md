With `codext`, the `codecs` library has multiple new encodings in addition to [the native ones](https://docs.python.org/3.8/library/codecs.html#standard-encodings), like presented hereafter.

Unless explicitely specified, each codec supports writing to and reading from a file.

!!! warning "Lossy conversion"
    
    Some encodings are lossy, meaning that it is not always possible to decode back to the exact start string. This should be considered especially when chaining codecs.

-----

### Ascii85

This encoding relies on the `base64` library and is only supported in Python 3.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`ascii85` | text <-> ascii85 | none | Python 3 only

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

### Baudot

It supports various formats such as CCITT-1 and CCITT-2, ITA1 and ITA2, and some others.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`baudot` | text <-> text | Baudot code bits | `baudot-ccitt1`, `baudot_ccitt2_lsb`, ... | supports CCITT-1, CCITT-2, EU/FR, ITA1, ITA2, MTK-2 (Python3 only), UK, ...
`baudot-spaced` | text <-> Baudot code groups of bits | `baudot-spaced-ita1_lsb`, `baudot_spaced_ita2_msb`, ... | groups of 5 bits are whitespace-separated
`baudot-tape` | text <-> Baudot code tape | `baudot-tape-mtk2`, `baudot_tape_murray`, ... | outputs a string that looks like a perforated tape

!!! note "LSB / MSB"
    
    "`_lsb`" or "`_msb`" can be specified in the codec name to set the bits order. If not specified, it defaults to MSB.


```python
>>> codext.encode("12345", "baudot-fr")
'010000000100010001000010100111'
>>> codext.decode("010000000100010001000010100111", "baudot-fr")
'12345'
```

```python
>>> codext.encode("TEST", "baudot-spaced_uk")
'10101 00010 10100 10101'
>>> codext.decode("10101 00010 10100 10101", "baudot-spaced_uk")
'TEST'
```

```python
>>> s = codext.encode("HELLO WORLD!", "baudot-tape_ita2")
>>> print(s)
***.**
* *.  
   . *
*  .* 
*  .* 
** .  
  *.  
*  .**
** .  
 * .* 
*  .* 
 * . *
** .**
 **. *
>>> codext.decode(s, "baudot-tape_ita2")
'HELLO WORLD!'
```

-----

### Braille

It supports letters, digits and some special characters.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`braille` | text <-> braille symbols | | Python 3 only

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
`dna` (rule 1) | text <-> DNA-1 | `dna1`, `dna-1`, `dna_1` | 
`dna` (rule X) | text <-> DNA-X | ... | 
`dna` (rule 8) | text <-> DNA-8 | `dna8`, `dna-8`, `dna_8` | 

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
`leetspeak` | text <-> leetspeak encoded text | `leet`, `1337`, `leetspeak` | based on minimalistic elite speaking rules

```python
>>> codext.encode("this is a test", "leetspeak")
'7h15 15 4 7357'
>>> codext.decode("7h15 15 4 7357", "leetspeak")
'ThIS IS A TEST'
```

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
`morse` | text <-> morse encoded text | none | uses whitespace as a separator, dynamic tokens mapping ; we can define a mapping of encoding's tokens (original tokens: `/-.`)

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

### Octal

This simple codec converts characters into their octal values.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`octal` | text <-> octal digits | `octals` | groups of 3-chars octal values when encoded
`octal-spaced` | text <-> spaced octal digits | `octals-spaced` | whitespace-separated suite of variable-length groups of octal digits when encoded

```python
>>> codext.encode("this is a test", "octal")
'164150151163040151163040141040164145163164'
>>> codext.decode("164150151163040151163040141040164145163164", "octals")
'this is a test'
```

```python
>>> codext.encode("this is a test", "octal-spaced")
'164 150 151 163 40 151 163 40 141 40 164 145 163 164'
>>> codext.decode("164 150 151 163 40 151 163 40 141 40 164 145 163 164", "octals-spaced")
'this is a test'
```

-----

### Ordinal

This simple codec converts characters into their ordinals.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`ordinal` | text <-> ordinal digits | `ordinals` | groups of 3-chars ordinal values when encoded
`ordinal-spaced` | text <-> spaced ordinal digits | `ordinals-spaced` | whitespace-separated suite of variable-length groups of ordinal digits when encoded

```python
>>> codext.encode("this is a test", "ordinal")
'116104105115032105115032097032116101115116'
>>> codext.decode("116104105115032105115032097032116101115116", "ordinals")
'this is a test'
```

```python
>>> codext.encode("this is a test", "ordinal-spaced")
'116 104 105 115 32 105 115 32 97 32 116 101 115 116'
>>> codext.decode("116 104 105 115 32 105 115 32 97 32 116 101 115 116", "ordinals-spaced")
'this is a test'
```

-----

### Radio Alphabet

This is also known as the [NATO phonetic alphabet](https://en.wikipedia.org/wiki/NATO_phonetic_alphabet).

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`radio` | text <-> radio alphabet words | `military_alphabet`, `nato-phonetic-alphabet`, `radio-alphabet` | 

```python
>>> codext.encode("foobar", "nato_phonetic_alphabet")
'Foxtrot Oscar Oscar Bravo Alpha Romeo'
>>> codext.decode("Foxtrot Oscar Oscar Bravo Alpha Romeo", "radio-alphabet")
'FOOBAR'
```

-----

### Resistor Color Codes

This uses the [electronic color code](https://en.wikipedia.org/wiki/Electronic_color_code#Resistor_color-coding) to encode digits, displaying colors in the terminal with ANSI color codes.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`resistor` | text <-> resistor colors | `resistors-color`, `resistor_color_code` | visually, it only works in a terminal supporting ANSI color codes

```python
>>> codext.encode("1234", "resistor")
'\x1b[48;5;130m \x1b[0;00m\x1b[48;5;1m \x1b[0;00m\x1b[48;5;214m \x1b[0;00m\x1b[48;5;11m \x1b[0;00m'
>>> codext.decode("\x1b[48;5;130m \x1b[0;00m\x1b[48;5;1m \x1b[0;00m\x1b[48;5;214m \x1b[0;00m\x1b[48;5;11m \x1b[0;00m", "resistors_color")
'1234'
```

-----

### SMS (T9)

This codec.

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

### URL

This handles URL encoding, regardless of the case when decoding and with no error.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`url` | text <-> URL encoded text | `url`, `urlencode` | 

```python
>>> codecs.encode("?=this/is-a_test/../", "url")
'%3F%3Dthis%2Fis-a_test%2F%2E%2E%2F'
>>> codext.decode("%3F%3Dthis%2Fis-a_test%2F%2E%2E%2F", "urlencode")
'?=this/is-a_test/../'
>>> codext.decode("%3f%3dthis%2fis-a_test%2f%2e%2e%2f", "urlencode")
'?=this/is-a_test/../'
```

-----

### Whitespaces

This simple encoding replaces zeros and ones of the binary version of the input text with spaces and tabs. It is supported either with its original mapping or with the inverted mapping.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`whitespace` | text <-> whitespaces and tabs | `whitespaces?-inv(erted)?` | The default encoding uses tabs for zeros and spaces for ones
`whitespace_after_before` | text <-> whitespaces[letter]whitespaces | | This codec encodes characters as new characters with whitespaces before and after according to an equation described in the codec name (e.g. "`whitespace+2*after-3*before`")

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
