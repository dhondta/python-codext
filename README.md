<h1 align="center">CodExt <a href="https://twitter.com/intent/tweet?text=CodExt%20-%20Encoding%2Fdecoding%20anything.%0D%0APython%20library%20extending%20the%20native%20codecs%20library%20with%20many%20new%20encodings%20and%20providing%20CLI%20tools%20with%20a%20guess%20feature%20based%20on%20AI.%0D%0Ahttps%3a%2f%2fgithub%2ecom%2fdhondta%2fpython-codext%0D%0A&hashtags=python,programming,encodings,codecs,cryptography,morse,base,ctftools"><img src="https://img.shields.io/badge/Tweet--lightgrey?logo=twitter&style=social" alt="Tweet" height="20"/></a></h1>
<h3 align="center">Encode/decode anything.</h3>

[![PyPi](https://img.shields.io/pypi/v/codext.svg)](https://pypi.python.org/pypi/codext/)
[![Read The Docs](https://readthedocs.org/projects/python-codext/badge/?version=latest)](https://python-codext.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.com/dhondta/python-codext.svg?branch=master)](https://travis-ci.com/dhondta/python-codext)
[![Coverage Status](https://coveralls.io/repos/github/dhondta/python-codext/badge.svg?branch=master)](https://coveralls.io/github/dhondta/python-codext?branch=master)
[![Python Versions](https://img.shields.io/pypi/pyversions/codext.svg)](https://pypi.python.org/pypi/codext/)
[![Requirements Status](https://requires.io/github/dhondta/python-codext/requirements.svg?branch=master)](https://requires.io/github/dhondta/python-codext/requirements/?branch=master)
[![Known Vulnerabilities](https://snyk.io/test/github/dhondta/python-codext/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/dhondta/python-codext?targetFile=requirements.txt)
[![License](https://img.shields.io/pypi/l/codext.svg)](https://pypi.python.org/pypi/codext/)

This library extends the native [`codecs`](https://docs.python.org/3/library/codecs.html) library (namely for adding new custom encodings and character mappings) and provides a myriad of new encodings (static or parametrized, like `rot` or `xor`), hence its named combining *CODecs EXTension*.

```sh
$ pip install codext
```

## :mag: Demonstrations

<p align="center"><img src="https://raw.githubusercontent.com/dhondta/python-codext/master/docs/demos/using-codext.gif" alt="Using CodExt from the command line"></p>
<p align="center"><img src="https://raw.githubusercontent.com/dhondta/python-codext/master/docs/demos/using-bases.gif" alt="Using base tools from the command line"></p>
<p align="center"><img src="https://raw.githubusercontent.com/dhondta/python-codext/master/docs/demos/using-debase.gif" alt="Using the debase command line tool"></p>

## :computer: Usage (main CLI tool) <a href="https://twitter.com/intent/tweet?text=CodExt%20-%20Encode%2Fdecode%20anything.%0D%0APython%20tool%20for%20encoding%20and%20decoding%20almost%20anything,%20including%20a%20guess%20feature%20based%20on%20AI.%0D%0Ahttps%3a%2f%2fgithub%2ecom%2fdhondta%2fpython-codext%0D%0A&hashtags=python,encodings,codecs,cryptography,morse,base,stegano,steganography,ctftools"><img src="https://img.shields.io/badge/Tweet%20(codext)--lightgrey?logo=twitter&style=social" alt="Tweet on codext" height="20"/></a>

```session
$ codext -i test.txt encode dna-1
GTGAGCGGGTATGTGA

$ echo -en "test" | codext encode morse
- . ... -

$ echo -en "test" | codext encode braille
⠞⠑⠎⠞

$ echo -en "test" | codext encode base100
👫👜👪👫
```

Chaining codecs:

```sh
$ echo -en "Test string" | codext encode reverse
gnirts tseT

$ echo -en "Test string" | codext encode reverse morse
--. -. .. .-. - ... / - ... . -

$ echo -en "Test string" | codext encode reverse morse dna-2
AGTCAGTCAGTGAGAAAGTCAGTGAGAAAGTGAGTGAGAAAGTGAGTCAGTGAGAAAGTCAGAAAGTGAGTGAGTGAGAAAGTTAGAAAGTCAGAAAGTGAGTGAGTGAGAAAGTGAGAAAGTC

$ echo -en "Test string" | codext encode reverse morse dna-2 octal
101107124103101107124103101107124107101107101101101107124103101107124107101107101101101107124107101107124107101107101101101107124107101107124103101107124107101107101101101107124103101107101101101107124107101107124107101107124107101107101101101107124124101107101101101107124103101107101101101107124107101107124107101107124107101107101101101107124107101107101101101107124103

$ echo -en "AGTCAGTCAGTGAGAAAGTCAGTGAGAAAGTGAGTGAGAAAGTGAGTCAGTGAGAAAGTCAGAAAGTGAGTGAGTGAGAAAGTTAGAAAGTCAGAAAGTGAGTGAGTGAGAAAGTGAGAAAGTC" | codext -d dna-2 morse reverse
test string
```

## :computer: Usage (base CLI tool) <a href="https://twitter.com/intent/tweet?text=Debase%20-%20Decode%20any%20multi-layer%20base-encoded%20string.%0D%0APython%20tool%20for%20decoding%20any%20base-encoded%20string,%20even%20when%20encoded%20with%20multiple%20layers.%0D%0Ahttps%3a%2f%2fgithub%2ecom%2fdhondta%2fpython-codext%0D%0A&hashtags=python,base,encodings,codecs,cryptography,stegano,steganography,ctftools"><img src="https://img.shields.io/badge/Tweet%20(debase)--lightgrey?logo=twitter&style=social" alt="Tweet on debase" height="20"/></a>

```session
$ echo "Test string !" | base122
*.7!ft9�-f9Â

$ echo "Test string !" | base91 
"ONK;WDZM%Z%xE7L

$ echo "Test string !" | base91 | base85
B2P|BJ6A+nO(j|-cttl%

$ echo "Test string !" | base91 | base85 | base36 | base58-flickr
QVx5tvgjvCAkXaMSuKoQmCnjeCV1YyyR3WErUUErFf

$ echo "Test string !" | base91 | base85 | base36 | base58-flickr | base58-flickr -d | base36 -d | base85 -d | base91 -d
Test string !
```

```session
$ echo "Test string !" | base91 | base85 | base36 | base58-flickr | debase -m 3
Test string !

$ echo "Test string !" | base91 | base85 | base36 | base58-flickr | debase -f Test
Test string !
```

## :computer: Usage (Python)

Getting the list of available codecs:

```python
>>> import codext

>>> codext.list()
['ascii85', 'base85', 'base100', 'base122', ..., 'tomtom', 'dna', 'html', 'markdown', 'url', 'resistor', 'sms', 'whitespace', 'whitespace-after-before']

>>> codext.encode("this is a test", "base58-bitcoin")
'jo91waLQA1NNeBmZKUF'

>>> codext.encode("this is a test", "base58-ripple")
'jo9rA2LQwr44eBmZK7E'

>>> codext.encode("this is a test", "base58-url")
'JN91Wzkpa1nnDbLyjtf'

>>> codecs.encode("this is a test", "base100")
'👫👟👠👪🐗👠👪🐗👘🐗👫👜👪👫'

>>> codecs.decode("👫👟👠👪🐗👠👪🐗👘🐗👫👜👪👫", "base100")
'this is a test'

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

## :page_with_curl: List of codecs

**Codec** | **Conversions** | **Comment**
:---: | :---: | ---
`a1z26` | text <-> alphabet order numbers | keeps words whitespace-separated and uses a custom character separator
`affine` | text <-> affine ciphertext | aka Affine Cipher
`ascii85` | text <-> ascii85 encoded text | Python 3 only
`atbash` | text <-> Atbash ciphertext | aka Atbash Cipher
`bacon` | text <-> Bacon ciphertext | aka Baconian Cipher
`barbie-N` | text <-> barbie ciphertext | aka Barbie Typewriter (N belongs to [1, 4])
`baseXX` | text <-> baseXX | see [base encodings](https://python-codext.readthedocs.io/en/latest/enc/base.html) (incl base32, 36, 45, 58, 62, 63, 64, 91, 100, 122)
`baudot` | text <-> Baudot code bits | supports CCITT-1, CCITT-2, EU/FR, ITA1, ITA2, MTK-2 (Python3 only), UK, ...
`bcd` | text <-> binary coded decimal text | encodes characters from their (zero-left-padded) ordinals
`braille` | text <-> braille symbols | Python 3 only
`citrix` | text <-> Citrix CTX1 ciphertext | aka Citrix CTX1 passord encoding
`dna` | text <-> DNA-N sequence | implements the 8 rules of DNA sequences (N belongs to [1,8])
`excess3` | text <-> XS3 encoded text | uses Excess-3 (aka Stibitz code) binary encoding to convert characters from their ordinals
`gray` | text <-> gray encoded text | aka reflected binary code
`gzip` | text <-> Gzip-compressed text | standard Gzip compression/decompression
`html` | text <-> HTML entities | implements entities according to [this reference](https://dev.w3.org/html5/html-author/charref)
`ipsum` | text <-> latin words | aka lorem ipsum
`klopf` | text <-> klopf encoded text | Polybius square with trivial alphabetical distribution
`leetspeak` | text <-> leetspeak encoded text | based on minimalistic elite speaking rules
`letter-indices` | text <-> text with letter indices | encodes consonants and/or vowels with their corresponding indices
`lz77` | text <-> LZ77-compressed text | compresses the given data with the algorithm of Lempel and Ziv of 1977
`lz78` | text <-> LZ78-compressed text | compresses the given data with the algorithm of Lempel and Ziv of 1978
`manchester` | text <-> manchester encoded text | XORes each bit of the input with `01`
`markdown` | markdown --> HTML | unidirectional
`morse` | text <-> morse encoded text | uses whitespace as a separator
`navajo` | text <-> Navajo | only handles letters (not full words from the Navajo dictionary)
`octal` | text <-> octal digits | dummy octal conversion (converts to 3-digits groups)
`ordinal` | text <-> ordinal digits | dummy character ordinals conversion (converts to 3-digits groups)
`pkzip_deflate` | text <-> deflated text | standard Zip-deflate compression/decompression
`pkzip_bzip2` | text <-> Bzipped text | standard BZip2 compression/decompression
`pkzip_lzma` | text <-> LZMA-compressed text | standard LZMA compression/decompression
`radio` | text <-> radio words | aka NATO or radio phonetic alphabet
`resistor` | text <-> resistor colors | aka resistor color codes
`rot` | text <-> rot(N) ciphertext | aka Caesar cipher (N belongs to [1,25])
`rotate` | text <-> N-bits-rotated text | rotates characters by the specified number of bits ; Python 3 only
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


## :clap:  Supporters

[![Stargazers repo roster for @dhondta/python-codext](https://reporoster.com/stars/dark/dhondta/python-codext)](https://github.com/dhondta/python-codext/stargazers)

[![Forkers repo roster for @dhondta/python-codext](https://reporoster.com/forks/dark/dhondta/python-codext)](https://github.com/dhondta/python-codext/network/members)

<p align="center"><a href="#"><img src="https://img.shields.io/badge/Back%20to%20top--lightgrey?style=social" alt="Back to top" height="20"/></a></p>
