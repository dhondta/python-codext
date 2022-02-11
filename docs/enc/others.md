## Others

All kinds of other codecs are categorized in "*Others*".

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

### Letter indices

This encodes consonants and/or vowels with their respective indices. This codec is case insensitive, strips white spaces and only applies to letters.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`consonant-indices` | text <-> text with consonant indices | `consonants_indices`, `consonants_index` | while decoding, searches from the longest match, possibly not producing the original input
`vowel-indices` | text <-> text with vowel indices | `vowels_indices`, `vowels_index` | 
`consonant-vowel-indices` | text <-> text with consonant and vowel indices | `consonants-vowels_index` | prefixes consonants with `C` and vowels with `V`

```python
>>> codext.encode("This is a test", "consonant-index")
'166I15I15A16E1516'
>>> codext.decode("166I15I15A16E1516", "consonant-index")
'THISISATEST'
```

```python
>>> codext.encode("This is a test", "vowel-index")
'TH3S3S1T2ST'
>>> codext.decode("TH3S3S1T2ST", "vowel-index")
'THISISATEST'
```

```python
>>> codext.encode("This is a test", "consonant-vowel-index")
'C16C6V3C15V3C15V1C16V2C15C16'
>>> codext.decode("C16C6V3C15V3C15V1C16V2C15C16", "consonant-vowel-index")
'THISISATEST'
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

