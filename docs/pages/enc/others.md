## Others

All kinds of other codecs are categorized in "*Others*".

-----

### BinHex

BinHex 4.0 (`.hqx`) is the binary-to-text encoding of the classic Mac OS. The data is stored as the data fork of a file (named "`-`", with unknown type and creator codes and an empty resource fork) whose header and forks are protected with CRCs. This stream is compressed with run-length encoding, then encoded with 6 bits per character, framed by "`:`" and wrapped in lines of 64 characters after the "`(This file must be converted with BinHex 4.0)`" line.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`binhex` | data <-> BinHex 4.0 data | `binhex4`, `binhex-4.0`, `hqx` | decoding ignores the text around the data, checks the CRCs and returns the data fork

```python
>>> codext.encode("Hello", "binhex")
'(This file must be converted with BinHex 4.0)\n\n:!5d!2j!)!*!&"3#3"$X55\'9XE\'r,eJ!!:\n'
>>> codext.decode(":!5d!2j!)!*!&\"3#3\"$X55'9XE'r,eJ!!:", "hqx")
'Hello'
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

### Dvorak

The [Dvorak Simplified Keyboard](https://en.wikipedia.org/wiki/Dvorak_keyboard_layout), patented in 1936, rearranges the letters and some punctuation of the QWERTY layout (US). Encoding replaces each character by the one of the same key with the Dvorak layout (as when typing with the QWERTY layout on a computer set to Dvorak), while decoding does the opposite. This [permutation of 35 keys](https://www.montefischer.com/2021/03/21/dvorak-group-action.html) (letters and the `-`, `=`, `[`, `]`, `;`, `'`, `,`, `.` and `/` keys, with their shifted characters) gets back to the text after 210 encodings.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`dvorak` | text <-> text typed with the Dvorak layout | `qwerty-dvorak`, `qwerty_to_dvorak` | other characters kept as is

```python
>>> codext.encode("Hello, World!", "dvorak")
'D.nnrw <rpne!'
>>> codext.decode("D.nnrw <rpne!", "dvorak")
'Hello, World!'
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

-----

### Soundex

[Soundex](https://www.archives.gov/research/census/soundex) indexes names by their sound, as used by the US National Archives: each word is written as its first letter followed by three digits for its next consonants (B, F, P and V give 1 ; C, G, J, K, Q, S, X and Z give 2 ; D and T give 3 ; L gives 4 ; M and N give 5 ; R gives 6), the vowels being dropped, the consecutive consonants with the same digit (including the first letter, or separated by H or W) giving a single digit, and the code being padded with zeros or truncated. Encoding replaces each word by its code, keeping the other characters. As Soundex is not reversible, decoding replaces each code by the most frequent word with this code from an English word list (9850 words, from the [lists of Ciphey](https://github.com/Ciphey/CipheyDists)), or, with the `-all` variant, by all these words in order of frequency.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`soundex` | text <-> Soundex codes | | decoding gives the most frequent English word for each code ; codes without word handled with the errors handling
`soundex-all` | text <-> Soundex codes | `soundex_all` | decoding gives all the English words for each code (e.g. `[world|worldwide|worlds]`)

!!! warning "Decoding"

    Decoding cannot give back the original words, only words with the same code (e.g. `Robert` gives `R163`, which gives `report`). Ciphey's own table of codes does not merge the first letter with the next consonant with the same digit (e.g. `cc` gives `C200` instead of `C000` and `Pfister` gives `P123` instead of `P236`), unlike the rules of the US National Archives followed by this codec.

```python
>>> codext.encode("Robert Rupert Pfister", "soundex")
'R163 R163 P236'
>>> codext.decode("R163 W643", "soundex")
'report world'
```

-----

### Telegraph

The [Chinese telegraph code](https://en.wikipedia.org/wiki/Chinese_telegraph_code), designed in 1871, sends Chinese characters by telegraph as groups of four digits (from `0000` to `9999`), as given in a codebook. Mainland China (with the simplified characters) and Taiwan (with the traditional characters) use different codebooks, taken from the [Unihan database](https://www.unicode.org/reports/tr38/#kMainlandTelegraph) of Unicode. Encoding gives the groups of four digits of the characters, separated by spaces, while decoding accepts groups separated by whitespaces or not.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`telegraph` | Chinese text <-> groups of 4 digits | `chinese-telegraph`, `telegraph-mainland` | codebook of Mainland China (7078 characters)
`telegraph-taiwan` | Chinese text <-> groups of 4 digits | `telegraph-tw` | codebook of Taiwan (9024 characters)

```python
>>> codext.encode("中文信息", "telegraph")
'0022 2429 0207 1873'
>>> codext.decode("5618 1947 0948", "telegraph-taiwan")
'蕭愛國'
```

-----

### XXencode

XXencode works like UUencode, but with an alphabet made of "`+`", "`-`", digits and letters only. Each line encodes up to 45 bytes and starts with the character holding its number of bytes ; the lines are framed by a `begin` line and an `end` line.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`xx` | data <-> XXencoded data | `xxencode`, `xx-encode`, `xx_codec` | decoding works with or without the `begin` and `end` lines

```python
>>> codext.encode("Cat", "xxencode")
'begin 666 -\n1Eq3o\n+\nend\n'
>>> codext.decode("1Eq3o", "xx")
'Cat'
```

-----

### yEnc

yEnc is the binary-to-text encoding of Usenet. Each byte is shifted by 42 and only the critical characters (NUL, LF, CR, "`=`", as well as TAB and SPACE at the beginning or the end of a line and "`.`" at the beginning of a line) are escaped with "`=`".

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`yenc` | data <-> yEnc-encoded data | `y-enc`, `y_enc` | raw data on a single line
`yenc-N` | data <-> yEnc-encoded data | | data in lines of N characters
`yenc-full` | data <-> yEnc-encoded data | `yenc-N-full` | data in lines of 128 (or N) characters, framed by the `=ybegin` header and the `=yend` trailer (size and CRC32)

When decoding, the header and the trailer are detected (the size and the CRC32 being checked) and line breaks are ignored, so that every form is decoded by any of these codecs.

```python
>>> codext.encode("Hello", "yenc")
'r\x8f\x96\x96\x99'
>>> codext.encode("Hello", "yenc-full")
'=ybegin line=128 size=5 name=-\r\nr\x8f\x96\x96\x99\r\n=yend size=5 crc32=f7d18982\r\n'
>>> codext.decode("=ybegin line=128 size=5 name=-\r\nr\x8f\x96\x96\x99\r\n=yend size=5 crc32=f7d18982\r\n", "yenc")
'Hello'
```
