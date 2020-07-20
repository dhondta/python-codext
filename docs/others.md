With `codext`, the `codecs` library has multiple new encodings in addition to [the native ones](https://docs.python.org/3.8/library/codecs.html#standard-encodings), like presented hereafter.

Unless explicitely specified, each codec supports writing to and reading from a file.

!!! warning "Lossy conversion"
    
    Some encodings are lossy, meaning that it is not always possible to decode back to the exact start string. This should be considered especially when chaining codecs.

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

### HTML Entities

This implements the full list of characters available at [this reference](https://dev.w3.org/html5/html-author/charref).

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`html` | text <-> HTML entities | `html-entity`, `html_entities` | implements entities according to [this reference](https://dev.w3.org/html5/html-author/charref)

```python
>>> codext.encode("Тħĩş Їś ą Ţêšŧ", "html")
'&Tcy;&hstrok;&itilde;&scedil; &YIcy;&sacute; &aogon; &Tcedil;&ecirc;&scaron;&tstrok;'
>>> codext.decode("&Tcy;&hstrok;&itilde;&scedil; &YIcy;&sacute; &aogon; &Tcedil;&ecirc;&scaron;&tstrok;", "html-entities")
'Тħĩş Їś ą Ţêšŧ'
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

