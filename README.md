[![PyPi](https://img.shields.io/pypi/v/codext.svg)](https://pypi.python.org/pypi/codext/)
[![Read The Docs](https://readthedocs.org/projects/python-codext/badge/?version=latest)](https://python-codext.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/dhondta/python-codext.svg?branch=master)](https://travis-ci.org/dhondta/python-codext)
[![Coverage Status](https://coveralls.io/repos/github/dhondta/python-codext/badge.svg?branch=master)](https://coveralls.io/github/dhondta/python-codext?branch=master)
[![Python Versions](https://img.shields.io/pypi/pyversions/codext.svg)](https://pypi.python.org/pypi/codext/)
[![Requirements Status](https://requires.io/github/dhondta/python-codext/requirements.svg?branch=master)](https://requires.io/github/dhondta/python-codext/requirements/?branch=master)
[![Known Vulnerabilities](https://snyk.io/test/github/dhondta/python-codext/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/dhondta/python-codext?targetFile=requirements.txt)
[![License](https://img.shields.io/pypi/l/codext.svg)](https://pypi.python.org/pypi/codext/)

# Codecs Extension

This library extends the native `codecs` library and provides some new encodings (static or parametrized, like `rot-N` or `xor-N`).

**Codec** | **Conversions** | **Comment**
:---: | :---: | ---
`affine` | text <-> affine ciphertext | aka Affine Cipher
`ascii85` | text <-> ascii85 encoded text | Python 3 only
`atbash` | text <-> Atbash ciphertext | aka Atbash Cipher
`bacon` | text <-> Bacon ciphertext | aka Baconian Cipher
`barbie-N` | text <-> barbie ciphertext | aka Barbie Typewriter (N belongs to [1, 4])
`baseXX` | text <-> baseXX | see [base encodings](https://python-codext.readthedocs.io/en/latest/base.html)
`baudot` | text <-> Baudot code bits | supports CCITT-1, CCITT-2, EU/FR, ITA1, ITA2, MTK-2 (Python3 only), UK, ...
`braille` | text <-> braille symbols | Python 3 only
`dna` | text <-> DNA-N sequence | implements the 8 rules of DNA sequences (N belongs to [1,8])
`html` | text <-> HTML entities | implements entities according to [this reference](https://dev.w3.org/html5/html-author/charref)
`leetspeak` | text <-> leetspeak encoded text | based on minimalistic elite speaking rules
`markdown` | markdown --> HTML | unidirectional
`morse` | text <-> morse encoded text | uses whitespace as a separator
`octal` | text <-> octal digits | dummy octal conversion (converts to 3-digits groups)
`ordinal` | text <-> ordinal digits | dummy character ordinals conversion (converts to 3-digits groups)
`radio` | text <-> radio words | aka NATO or radio phonetic alphabet
`resistor` | text <-> resistor colors | aka resistor color codes
`rot` | text <-> rot(N) ciphertext | aka Caesar cipher (N belongs to [1,25])
`scytale` | text <-> scytale ciphertext | encrypts with L, the number of letters on the rod (belongs to [1,[)
`shift` | text <-> shift(N) ciphertext | shift ordinals with N (belongs to [1,255])
`sms` | text <-> phone keystrokes | also called T9 code ; uses "`-`" as a separator for encoding, "`-`" or "`_`" or whitespace for decoding
`url` | text <-> URL encoded text | aka URL encoding
`xor` | text <-> XOR(N) ciphertext | XOR with a single byte (N belongs to [1,255])
`whitespace` | text <-> whitespaces and tabs | replaces bits with whitespaces and tabs

A few variants are also implemented.

**Codec** | **Conversions** | **Comment**
:---: | :---: | ---
`baudot-spaced` | text <-> Baudot code groups of bits | groups of 5 bits are whitespace-separated
`baudot-tape` | text <-> Baudot code tape | outputs a string that looks like a perforated tape
`octal-spaced` | text <-> octal digits (whitespace-separated) | dummy octal conversion
`ordinal-spaced` | text <-> ordinal digits (whitespace-separated) | dummy character ordinals conversion
`whitespace_after_before` | text <-> lines of whitespaces[letter]whitespaces | encodes characters as new characters with whitespaces before and after according to an equation described in the codec name (e.g. "`whitespace+2*after-3*before`")


## Setup

This library is available on [PyPi](https://pypi.python.org/pypi/codext/) and can be simply installed using Pip:

```sh
$ pip install codext
```

or

```sh
$ pip3 install codext
```

**Note**: Some more encodings are available when installing in Python 3.

## Usage (from terminal)

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

## Usage (within Python)

Example with Base58:

```python
>>> codext.encode("this is a test", "base58-bitcoin")
'jo91waLQA1NNeBmZKUF'
>>> codext.encode("this is a test", "base58-ripple")
'jo9rA2LQwr44eBmZK7E'
>>> codext.encode("this is a test", "base58-url")
'JN91Wzkpa1nnDbLyjtf'
```

Example with Base100 (emoji's):

```python
>>> codecs.encode("this is a test", "base100")
'👫👟👠👪🐗👠👪🐗👘🐗👫👜👪👫'
>>> codecs.decode("👫👟👠👪🐗👠👪🐗👘🐗👫👜👪👫", "base100")
'this is a test'
```

Example with DNA sequence encoding:

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

Example with morse:

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

Example with whitespaces before and after:

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

