<p align="center"><img src="https://github.com/dhondta/python-codext/raw/master/docs/imgs/logo.png"></p>
<h1 align="center">CodExt <a href="https://twitter.com/intent/tweet?text=CodExt%20-%20Encoding%2Fdecoding%20anything.%0D%0APython%20library%20extending%20the%20native%20codecs%20library%20with%20many%20new%20encodings%20and%20providing%20CLI%20tools%20with%20a%20guess%20feature%20based%20on%20AI.%0D%0Ahttps%3a%2f%2fgithub%2ecom%2fdhondta%2fpython-codext%0D%0A&hashtags=python,programming,encodings,codecs,cryptography,morse,base,ctftools"><img src="https://img.shields.io/badge/Tweet--lightgrey?logo=twitter&style=social" alt="Tweet" height="20"/></a></h1>
<h3 align="center">Encode/decode anything.</h3>

[![PyPi](https://img.shields.io/pypi/v/codext.svg)](https://pypi.python.org/pypi/codext/)
[![Read The Docs](https://readthedocs.org/projects/python-codext/badge/?version=latest)](https://python-codext.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.com/dhondta/python-codext.svg?branch=master)](https://travis-ci.com/dhondta/python-codext)
[![Coverage Status](https://coveralls.io/repos/github/dhondta/python-codext/badge.svg?branch=master)](https://coveralls.io/github/dhondta/python-codext?branch=master)
[![Python Versions](https://img.shields.io/pypi/pyversions/codext.svg)](https://pypi.python.org/pypi/codext/)
[![Requirements Status](https://requires.io/github/dhondta/python-codext/requirements.svg?branch=master)](https://requires.io/github/dhondta/python-codext/requirements/?branch=master)
[![Known Vulnerabilities](https://snyk.io/test/github/dhondta/python-codext/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/dhondta/python-codext?targetFile=requirements.txt)
[![DOI](https://zenodo.org/badge/236679865.svg)](https://zenodo.org/badge/latestdoi/236679865)
[![License](https://img.shields.io/pypi/l/codext.svg)](https://pypi.python.org/pypi/codext/)

[**CodExt**](https://github.com/dhondta/python-codext) is a (Python2-3 compatible) library that extends the native [`codecs`](https://docs.python.org/3/library/codecs.html) library (namely for adding new custom encodings and character mappings) and provides **120+ new codecs**, hence its name combining *CODecs EXTension*. It also features a **guess mode** for decoding multiple layers of encoding and **CLI tools** for convenience.

```sh
$ pip install codext
```

Want to contribute a new codec ?    |     Want to contribute a new macro ?
:----------------------------------:|:------------------------------------:
Check the [documentation](https://python-codext.readthedocs.io/en/latest/howto.html) first<br>Then [PR](https://github.com/dhondta/python-codext/pulls) your new codec | [PR](https://github.com/dhondta/python-codext/pulls) your updated version of [`macros.json`](https://github.com/dhondta/python-codext/blob/master/codext/macros.json)

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

### Chaining codecs

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

### Using macros

```sh
$ codext add-macro my-encoding-chain gzip base63 lzma base64

$ codext list macros
example-macro, my-encoding-chain

$ echo -en "Test string" | codext encode my-encoding-chain
CQQFAF0AAIAAABuTgySPa7WaZC5Sunt6FS0ko71BdrYE8zHqg91qaqadZIR2LafUzpeYDBalvE///ug4AA==

$ codext remove-macro my-encoding-chain

$ codext list macros
example-macro
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

#### BaseXX

- [X] `ascii85`: classical ASCII85 (Python3 only)
- [X] `baseN`: see [base encodings](https://python-codext.readthedocs.io/en/latest/enc/base.html) (incl base32, 36, 45, 58, 62, 63, 64, 91, 100, 122)
- [X] `base-genericN`: see [base encodings](https://python-codext.readthedocs.io/en/latest/enc/base.html) ; supports any possible base

#### Binary

- [X] `baudot`: supports CCITT-1, CCITT-2, EU/FR, ITA1, ITA2, MTK-2 (Python3 only), UK, ...
- [X] `baudot-spaced`: variant of `baudot` ; groups of 5 bits are whitespace-separated
- [X] `baudot-tape`: variant of `baudot` ; outputs a string that looks like a perforated tape
- [X] `bcd`: _Binary Coded Decimal_, encodes characters from their (zero-left-padded) ordinals
- [X] `bcd-extended0`: variant of `bcd` ; encodes characters from their (zero-left-padded) ordinals using prefix bits `0000`
- [X] `bcd-extended1`: variant of `bcd` ; encodes characters from their (zero-left-padded) ordinals using prefix bits `1111`
- [X] `excess3`: uses Excess-3 (aka Stibitz code) binary encoding to convert characters from their ordinals
- [X] `gray`: aka reflected binary code
- [X] `manchester`: XORes each bit of the input with `01`
- [X] `manchester-inverted`: variant of `manchester` ; XORes each bit of the input with `10`
- [X] `rotateN`: rotates characters by the specified number of bits (*N* belongs to [1, 7] ; Python 3 only)

#### Common

- [X] `a1z26`: keeps words whitespace-separated and uses a custom character separator
- [X] `cases`: set of case-related encodings (including camel-, kebab-, lower-, pascal-, upper-, snake- and swap-case, slugify, capitalize, title)
- [X] `dummy`: set of simple encodings (including replace, reverse, word-reverse, substite and strip-spaces)
- [X] `octal`: dummy octal conversion (converts to 3-digits groups)
- [X] `octal-spaced`: variant of `octal` ; dummy octal conversion, handling whitespace separators
- [X] `ordinal`: dummy character ordinals conversion (converts to 3-digits groups)
- [X] `ordinal-spaced`: variant of `ordinal` ; dummy character ordinals conversion, handling whitespace separators

#### Compression

- [X] `gzip`: standard Gzip compression/decompression
- [X] `lz77`: compresses the given data with the algorithm of Lempel and Ziv of 1977
- [X] `lz78`: compresses the given data with the algorithm of Lempel and Ziv of 1978
- [X] `pkzip_deflate`: standard Zip-deflate compression/decompression
- [X] `pkzip_bzip2`: standard BZip2 compression/decompression
- [X] `pkzip_lzma`: standard LZMA compression/decompression

> :warning: Compression functions are of course definitely **NOT** encoding functions ; they are implemented for leveraging the `.encode(...)` API from `codecs`.

#### Cryptography

- [X] `affine`: aka Affine Cipher
- [X] `atbash`: aka Atbash Cipher
- [X] `bacon`: aka Baconian Cipher
- [X] `barbie-N`: aka Barbie Typewriter (*N* belongs to [1, 4])
- [X] `citrix`: aka Citrix CTX1 passord encoding
- [X] `rotN`: aka Caesar cipher (*N* belongs to [1,25])
- [X] `scytaleN`: encrypts using the number of letters on the rod (*N* belongs to [1,[)
- [X] `shiftN`: shift ordinals (*N* belongs to [1,255])
- [X] `xorN`: XOR with a single byte (*N* belongs to [1,255])

> :warning: Crypto functions are of course definitely **NOT** encoding functions ; they are implemented for leveraging the `.encode(...)` API from `codecs`.

#### Hashing

- [X] `blake`: includes BLAKE2b and BLAKE2s (Python 3 only ; relies on `hashlib`)
- [X] `checksums`: includes Adler32 and CRC32 (relies on `zlib`)
- [X] `crypt`: Unix's crypt hash for passwords (Python 3 and Unix only ; relies on `crypt`)
- [X] `md`: aka Message Digest ; includes MD4 and MD5 (relies on `hashlib`)
- [X] `sha`: aka Secure Hash Algorithms ; includes SHA1, 224, 256, 384, 512 (Python2/3) but also SHA3-224, -256, -384 and -512 (Python 3 only ; relies on `hashlib`)
- [X] `shake`: aka SHAKE hashing (Python 3 only ; relies on `hashlib`)

> :warning: Hash functions are of course definitely **NOT** encoding functions ; they are implemented for convenience with the `.encode(...)` API from `codecs` and useful for chaning codecs.

#### Languages

- [X] `braille`: well-known braille language (Python 3 only)
- [X] `ipsum`: aka lorem ipsum
- [X] `galactic`: aka galactic alphabet or Minecraft enchantment language (Python 3 only)
- [X] `leetspeak`: based on minimalistic elite speaking rules
- [X] `morse`: uses whitespace as a separator
- [X] `navajo`: only handles letters (not full words from the Navajo dictionary)
- [X] `radio`: aka NATO or radio phonetic alphabet
- [X] `southpark`: converts letters to Kenny's language from Southpark (whitespace is also handled)
- [X] `southpark-icase`: case insensitive variant of `southpark`
- [X] `tap`: converts text to tap/knock code, commonly used by prisoners
- [X] `tomtom`: similar to `morse`, using slashes and backslashes

#### Others

- [X] `dna`: implements the 8 rules of DNA sequences (N belongs to [1,8])
- [X] `html`: implements entities according to [this reference](https://dev.w3.org/html5/html-author/charref)
- [X] `letter-indices`: encodes consonants and/or vowels with their corresponding indices
- [X] `markdown`: unidirectional encoding from Markdown to HTML
- [X] `url`: aka URL encoding

#### Steganography

- [X] `klopf`: aka Klopf code ; Polybius square with trivial alphabetical distribution
- [X] `resistor`: aka resistor color codes
- [X] `rick`: aka Rick cipher (in reference to Rick Astley's song "*Never gonna give you up*")
- [X] `sms`: also called _T9 code_ ; uses "`-`" as a separator for encoding, "`-`" or "`_`" or whitespace for decoding
- [X] `whitespace`: replaces bits with whitespaces and tabs
- [X] `whitespace_after_before`: variant of `whitespace` ; encodes characters as new characters with whitespaces before and after according to an equation described in the codec name (e.g. "`whitespace+2*after-3*before`")


## :clap:  Supporters

[![Stargazers repo roster for @dhondta/python-codext](https://reporoster.com/stars/dark/dhondta/python-codext)](https://github.com/dhondta/python-codext/stargazers)

[![Forkers repo roster for @dhondta/python-codext](https://reporoster.com/forks/dark/dhondta/python-codext)](https://github.com/dhondta/python-codext/network/members)

<p align="center"><a href="#"><img src="https://img.shields.io/badge/Back%20to%20top--lightgrey?style=social" alt="Back to top" height="20"/></a></p>
