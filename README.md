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
`ascii85` | Ascii85 <-> text | Python 3 only
`base16` | Base16 <-> text | 
`base32` | Base32 <-> text | 
`base64` | Base64 <-> text | 
`base85` | Base85 <-> text | Python 3 only
`base100` | Base100 <-> text | Python 3 only
`dna-N` | DNA-N <-> text | implements the 8 rules of DNA sequences (N belongs to [1,8])
`leetspeak` | leetspeak <-> text | based on minimalistic elite speaking rules
`markdown` | markdown --> HTML | unidirectional
`morse` | morse <-> text | uses whitespace as a separator
`nokia3310` | Nokia 3310 keystrokes <-> text | uses "`-`" as a separator for encoding, "`-`" or "`_`" or whitespace for decoding
`rot-N` | ROT(N) <-> text | aka Caesar cipher (N belongs to [1,25])
`xor-N` | XOR(N) <-> text | XOR with a single byte (N belongs to [1,255])


## Setup

This library is available on [PyPi](https://pypi.python.org/pypi/codext/) and can be simply installed using Pip:

```sh
pip install codext
```

or

```sh
pip3 install codext
```

## Usage

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
