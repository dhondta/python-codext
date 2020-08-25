[![PyPi](https://img.shields.io/pypi/v/codext.svg)](https://pypi.python.org/pypi/codext/)
[![Read The Docs](https://readthedocs.org/projects/python-codext/badge/?version=latest)](https://python-codext.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/dhondta/python-codext.svg?branch=master)](https://travis-ci.org/dhondta/python-codext)
[![Coverage Status](https://coveralls.io/repos/github/dhondta/python-codext/badge.svg?branch=master)](https://coveralls.io/github/dhondta/python-codext?branch=master)
[![Python Versions](https://img.shields.io/pypi/pyversions/codext.svg)](https://pypi.python.org/pypi/codext/)
[![Requirements Status](https://requires.io/github/dhondta/python-codext/requirements.svg?branch=master)](https://requires.io/github/dhondta/python-codext/requirements/?branch=master)
[![Known Vulnerabilities](https://snyk.io/test/github/dhondta/python-codext/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/dhondta/python-codext?targetFile=requirements.txt)
[![License](https://img.shields.io/pypi/l/codext.svg)](https://pypi.python.org/pypi/codext/)

# CODecs EXTension

This library extends the native `codecs` library (namely for adding new custom encodings and character mappings) and provides a myriad of new encodings (static or parametrized, like `rot` or `xor`).

## Setup

```sh
$ pip install codext
```

**Note**: Some encodings are available in Python 3 only.

## Usage (CLI tool)

```sh
$ codext dna-1 -i test.txt
GTGAGCGGGTATGTGA
$ echo -en "test" | codext morse
- . ... -
```

Python 3 (includes Ascii85, Base85, Base100 and braille):

```sh
$ echo -en "test" | codext braille
⠞⠑⠎⠞
$ echo -en "test" | codext base100
👫👜👪👫
```

Using codecs chaining:

```sh
$ echo -en "Test string" | codext reverse
gnirts tseT
$ echo -en "Test string" | codext reverse morse
--. -. .. .-. - ... / - ... . -
$ echo -en "Test string" | codext reverse morse dna-2
AGTCAGTCAGTGAGAAAGTCAGTGAGAAAGTGAGTGAGAAAGTGAGTCAGTGAGAAAGTCAGAAAGTGAGTGAGTGAGAAAGTTAGAAAGTCAGAAAGTGAGTGAGTGAGAAAGTGAGAAAGTC
$ echo -en "Test string" | codext reverse morse dna-2 octal
101107124103101107124103101107124107101107101101101107124103101107124107101107101101101107124107101107124107101107101101101107124107101107124103101107124107101107101101101107124103101107101101101107124107101107124107101107124107101107101101101107124124101107101101101107124103101107101101101107124107101107124107101107124107101107101101101107124107101107101101101107124103
$ echo -en "AGTCAGTCAGTGAGAAAGTCAGTGAGAAAGTGAGTGAGAAAGTGAGTCAGTGAGAAAGTCAGAAAGTGAGTGAGTGAGAAAGTTAGAAAGTCAGAAAGTGAGTGAGTGAGAAAGTGAGAAAGTC" | codext -d dna-2 morse reverse
test string
```

## Usage (Python)

Getting the list of available codecs:

```python
>>> import codext
>>> codext.list()
['ascii85', 'base85', 'base100', 'base122', ..., 'tomtom', 'dna', 'html', 'markdown', 'url', 'resistor', 'sms', 'whitespace', 'whitespace-after-before']
```

Usage examples:

```python
>>> codext.encode("this is a test", "base58-bitcoin")
'jo91waLQA1NNeBmZKUF'
>>> codext.encode("this is a test", "base58-ripple")
'jo9rA2LQwr44eBmZK7E'
>>> codext.encode("this is a test", "base58-url")
'JN91Wzkpa1nnDbLyjtf'
```

```python
>>> codecs.encode("this is a test", "base100")
'👫👟👠👪🐗👠👪🐗👘🐗👫👜👪👫'
>>> codecs.decode("👫👟👠👪🐗👠👪🐗👘🐗👫👜👪👫", "base100")
'this is a test'
```

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

```python
>>> codecs.encode("this is a test", "morse")
'- .... .. ... / .. ... / .- / - . ... -'
>>> codecs.decode("- .... .. ... / .. ... / .- / - . ... -", "morse")
'this is a test'
>>> with open("morse.txt", 'w', encoding="morse") as f:
	f.write("this is a test")
14
>>> with open("morse.txt",encoding="morse") as f:
	f.read()
'this is a test'
```

```python
>>> codext.decode("""
      =            
              X         
   :            
      x         
  n  
    r 
        y   
      Y            
              y        
     p    
         a       
 `          
            n            
          |    
  a          
o    
       h        
          `            
          g               
           o 
   z      """, "whitespace-after+before")
'CSC{not_so_invisible}'
```

```python
>>> print(codext.encode("An example test string", "baudot-tape"))
***.**
   . *
***.* 
*  .  
   .* 
*  .* 
   . *
** .* 
***.**
** .**
   .* 
*  .  
* *. *
   .* 
* *.  
* *. *
*  .  
* *.  
* *. *
***.  
  *.* 
***.* 
 * .* 
```

## List of codecs

**Codec** | **Conversions** | **Comment**
:---: | :---: | ---
`affine` | text <-> affine ciphertext | aka Affine Cipher
`ascii85` | text <-> ascii85 encoded text | Python 3 only
`atbash` | text <-> Atbash ciphertext | aka Atbash Cipher
`bacon` | text <-> Bacon ciphertext | aka Baconian Cipher
`barbie-N` | text <-> barbie ciphertext | aka Barbie Typewriter (N belongs to [1, 4])
`baseXX` | text <-> baseXX | see [base encodings](https://python-codext.readthedocs.io/en/latest/base.html)
`baudot` | text <-> Baudot code bits | supports CCITT-1, CCITT-2, EU/FR, ITA1, ITA2, MTK-2 (Python3 only), UK, ...
`bcd` | text <-> binary coded decimal text | encodes characters from their (zero-left-padded) ordinals
`braille` | text <-> braille symbols | Python 3 only
`dna` | text <-> DNA-N sequence | implements the 8 rules of DNA sequences (N belongs to [1,8])
`excess3` | text <-> XS3 encoded text | uses Excess-3 (aka Stibitz code) binary encoding to convert characters from their ordinals
`gray` | text <-> gray encoded text | aka reflected binary code
`html` | text <-> HTML entities | implements entities according to [this reference](https://dev.w3.org/html5/html-author/charref)
`leetspeak` | text <-> leetspeak encoded text | based on minimalistic elite speaking rules
`letter-indices` | text <-> text with letter indices | encodes consonants and/or vowels with their corresponding indices
`manchester` | text <-> manchester encoded text | XORes each bit of the input with `01`
`markdown` | markdown --> HTML | unidirectional
`morse` | text <-> morse encoded text | uses whitespace as a separator
`navajo` | text <-> Navajo | only handles letters (not full words from the Navajo dictionary)
`octal` | text <-> octal digits | dummy octal conversion (converts to 3-digits groups)
`ordinal` | text <-> ordinal digits | dummy character ordinals conversion (converts to 3-digits groups)
`radio` | text <-> radio words | aka NATO or radio phonetic alphabet
`resistor` | text <-> resistor colors | aka resistor color codes
`rot` | text <-> rot(N) ciphertext | aka Caesar cipher (N belongs to [1,25])
`scytale` | text <-> scytale ciphertext | encrypts with L, the number of letters on the rod (belongs to [1,[)
`shift` | text <-> shift(N) ciphertext | shift ordinals with N (belongs to [1,255])
`sms` | text <-> phone keystrokes | also called T9 code ; uses "`-`" as a separator for encoding, "`-`" or "`_`" or whitespace for decoding
`southpark` | text <-> Kenny's language | converts letters to Kenny's language from Southpark (whitespace is also handled)
`tomtom` | text <-> tom-tom encoded text | similar to `morse`, using slashes and backslashes
`url` | text <-> URL encoded text | aka URL encoding
`xor` | text <-> XOR(N) ciphertext | XOR with a single byte (N belongs to [1,255])
`whitespace` | text <-> whitespaces and tabs | replaces bits with whitespaces and tabs

A few variants are also implemented.

**Codec** | **Conversions** | **Comment**
:---: | :---: | ---
`baudot-spaced` | text <-> Baudot code groups of bits | groups of 5 bits are whitespace-separated
`baudot-tape` | text <-> Baudot code tape | outputs a string that looks like a perforated tape
`bcd-extended0` | text <-> BCD-extended text | encodes characters from their (zero-left-padded) ordinals using prefix bits `0000`
`bcd-extended1` | text <-> BCD-extended text | encodes characters from their (zero-left-padded) ordinals using prefix bits `1111`
`manchester-inverted` | text <-> manchester encoded text | XORes each bit of the input with `10`
`octal-spaced` | text <-> octal digits (whitespace-separated) | dummy octal conversion
`ordinal-spaced` | text <-> ordinal digits (whitespace-separated) | dummy character ordinals conversion
`southpark-icase` | text <-> Kenny's language | same as `southpark` but case insensitive
`whitespace_after_before` | text <-> lines of whitespaces[letter]whitespaces | encodes characters as new characters with whitespaces before and after according to an equation described in the codec name (e.g. "`whitespace+2*after-3*before`")

