`codext` also implements several simple cryptographic ciphers. But how does it relate to encoding while a key is required ? `codext` focuses on ciphers that have a weak key. With dynamically named encodings, it is then possible to define a bunch of encodings, one for each value of the key. For instance, Barbie Typewriter has a key with only 4 possible values. The `barbie` codec can then be `barbie-1`, ..., `barbie-4`.

!!! note "Available masks"
    
    Some cipher codecs use character masks to generate their alphabets. Groups of characters are indicated using a headin "`?`".
    
    `a`: printable characters
    `b`: all 8-bits chars
    `d`: digits
    `h`: lowercase hexadecimal
    `H`: uppercase hexadecimal
    `l`: lowercase letters
    `p`: punctuation characters
    `s`: whitespace
    `u`: uppercase letters
    
    When combining masks, only one occurrence of each character is taken in the final alphabet.
    
    So, for instance, the following masks yield the following alphabets:
    
    - `?l?u?d?s`: "`abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 `"
    - `?s.,?!?u?d`: "` .,?!ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789`"

-----

### ADFGX/ADFGVX Cipher

These ciphers were used by the German Army during World War I. Each character is first replaced by the labels of its row and column in a Polybius square, then the result is written in rows under a transposition keyword and read column by column, in the alphabetical order of the keyword letters. The square is filled with an optional keyword (without duplicates), then with the remaining characters of the alphabet.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`adfgx` | text <-> ADFGX ciphertext | `adfgx-cargo`, `adfgx_cipher-squarekey-cargo`, ... | 5x5 square with the labels `ADFGX` ; letters only, `J` is normalized to `I`
`adfgvx` | text <-> ADFGVX ciphertext | `adfgvx-privacy`, `adfgvx_cipher-squarekey-privacy`, ... | 6x6 square with the labels `ADFGVX` ; letters and digits

The codec name holds the optional square key, then the mandatory transposition key. Whitespaces are ignored (ciphertexts are usually written in groups of 5 letters) and the output is in uppercase. When encoding with `errors="replace"`, unsupported characters are encrypted as `X`.

```python
>>> codext.encode("Attack at once", "adfgx-btalpdhozkqfvsngicuxmrewy-cargo")
'FAXDFADDDGDGFFFAFAXAFAFX'
>>> codext.decode("FAXDF ADDDG DGFFF AFAX AFAFX", "adfgx-btalpdhozkqfvsngicuxmrewy-cargo")
'ATTACKATONCE'
>>> codext.encode("Attack at 1200am", "adfgvx-na1c3h8tb2ome5wrpd4f6g7i9j0klqsuvxyz-privacy")
'DGDDDAGDDGAFADDFDADVDVFAADVX'
>>> codext.decode(codext.encode("ATTACK AT DAWN", "adfgvx-secret-key"), "adfgvx-secret-key")
'ATTACKATDAWN'
```

-----

### AER-256

This toy cipher comes from online JavaScript encryption tools. The text is split into blocks of half the key length (rounded up), each block being read as a number made of its character codes. For each character of the key, its code is added to, divides or is subtracted from this number in turn, and the resulting floating-point numbers are written as JavaScript would and separated by `, `.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`aer256` | text <-> AER-256 ciphertext | `aer-256`, `aer_256` | parameterized with a mandatory key of at least 3 characters, e.g. `aer256-secret` ; only characters with a code below 256

!!! warning "Precision"

    As the computations are done with double-precision floats, as in JavaScript, keys of more than 12 characters give blocks that are too large to be decrypted exactly.

```python
>>> codext.encode("this is a test", "aer256-key")
'175.10891089108912, 147.33663366336634, -37.79207920792079, 171.86138613861385, 126.23762376237624, 175.0792079207921, 172.69306930693068'
>>> codext.decode("175.10891089108912, 147.33663366336634", "aer256-key")
'this'
```

-----

### Affine Cipher

This codec implements the Affine monoalphabetic substitution cipher. It is parametrizable with a mask for generating the alphabet and the parameters `a` and `b`. By default, it uses mask "`lus`" and parameters `a=1` and `b=2` but it can be set as in the examples hereafter.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`affine` | text <-> affine ciphertext | `affine`, `affine_cipher-?l?u?d?s-5,8`, `affine-?s.,?!?u?d-23,6`, ... | Mask-generated alphabet ; uses default mask "`?l?u?s`" with `a=1` and `b=2`

```python
>>> codext.encode("this is a test", "affine")
'vjkubkubcbvguv'
>>> codext.decode("vjkubkubcbvguv", "affine")
'this is a test'
>>> codext.encode("this is a test", "affine-?l?u?d?s-5,8")
'ORWJdWJdidOCJO'
>>> codext.decode("ORWJdWJdidOCJO", "affine-?l?u?d?s-5,8")
'this is a test'
>>> codext.encode("THIS IS A TEST", "affine-?s.,?!?u?d-5,8")
'AW1 D1 D2DAH A'
>>> codext.decode("AW1 D1 D2DAH A", "affine-?s.,?!?u?d-5,8")
'THIS IS A TEST'
```

!!! warning "Parameters `a` and `b`"
    
    Not all values are suitable for `a` and `b`. If a generated encoding map has mapping collisions, an exception is raised telling that `a` and `b` are bad.

-----

### ARMON-64

This toy cipher, a variant of [AER-256](#aer-256), comes from online JavaScript encryption tools. It works the same way, but with a fourth operation (the number is multiplied by 0.01 times the code of the key character) and with `+` as the separator.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`armon64` | text <-> ARMON-64 ciphertext | `armon-64`, `armon_64` | parameterized with a mandatory key of at least 3 characters, e.g. `armon64-secret` ; only characters with a code below 256

!!! warning "Precision"

    As with AER-256, keys of more than 12 characters give blocks that are too large to be decrypted exactly. Unlike the original JavaScript, decryption does not split numbers in exponent notation (e.g. `1e+21`) on their `+`.

```python
>>> codext.encode("this is a test", "armon64-test")
'210.18970297029702+177.9738613861386+-36.77544554455446+206.4225742574257+153.49900990099007+210.15524752475247+207.38732673267327'
>>> codext.decode("210.18970297029702+177.9738613861386", "armon64-test")
'this'
```

-----

### Atbash Cipher

It implements the monoalphabetic substitution cipher used for the Hebrew alphabet. By default, it considers the lowercase and uppercase letters, inverted per group, as the alphabet. It can also use a mask to extend it. Note that it does not generate any error for characters that are not part of the alphabet.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`atbash` | text <-> Atbash ciphertext | `atbash`, `atbash_cipher-?l?d?s`, ... | Mask-generated alphabet ; uses default mask "`?u?l`"

```python
>>> codext.encode("this is a test", "atbash")
'gsrh rh z gvhg'
>>> codext.encode("this is a test", "atbash-[?l?u?p?s]")
'.^]/a]/a a.{/.'
>>> codext.decode(".^]/a]/a a.{/.", "atbash_cipher_[?l?u?p?s]")
'this is a test'
```

-----

### ATOM-128

This toy cipher comes from online JavaScript encryption tools. It is Base64 with a shuffled alphabet, whose 65th character (`C`) is used for padding. As in the original JavaScript, the text is first escaped with JavaScript's `escape()` (e.g. a whitespace becomes `%20`), and unescaped after decoding.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`atom128` | text <-> ATOM-128 ciphertext | `atom-128`, `atom_128` | 

```python
>>> codext.encode("this is a test", "atom128")
'0IXBnsgsSI6tQfPqKDgsSoA6nmbC'
>>> codext.decode("0IXBnsgsSI6tQfPqKDgsSoA6nmbC", "atom-128")
'this is a test'
```

-----

### Autoclave/Autokey Cipher

This is a variant of the [Vigenere Cipher](#vigenere-cipher) using a key stream generated from the primer key and the message appended.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`autoclave` | text <-> Autoclave ciphertext | `autoclave-cipher`, `autokey` | 

```python
>>> codext.encode("This is a test !", "autoclave-test")
'Mlal bz i lmkt !'
>>> codext.decode("Mlal bz i lmkt !", "autokey_cipher-test")
'This is a test !'
```

-----

### Baconian Cipher

It support only letters.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`bacon` | text <-> Bacon ciphertext | `bacon-cipher`, `baconian_cipher`, `bacon-01`, `bacon-10` | Dynamic tokens mapping ; we can define a mapping of encoding's tokens (original tokens: `ab`)

```python
>>> codext.encode("this is a test", "bacon")
'baaba aabbb abaaa baaab  abaaa baaab  aaaaa  baaba aabaa baaab baaba'
>>> codext.encode("this is a test", "bacon_01")
'10010 00111 01000 10001  01000 10001  00000  10010 00100 10001 10010'
>>> codext.decode("-..-. ..--- .-... -...-  .-... -...-  .....  -..-. ..-.. -...- -..-.", "bacon_.-")
'THIS IS A TEST'
```

-----

### Barbie Typewriter

It implements the cipher for its 4 different keys.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`barbie` | text <-> Barbie ciphertext | `barbie-1`, `barbie-2`, `barbie-3`, `barbie-4`

```python
>>> codext.encode("this is a test", "barbie-1")
'hstf tf i hafh'
>>> codext.encode("this is a test", "barbie_3")
'fpsu su h ftuf'
>>> codext.decode("fpsu su h ftuf", "barbie-3")
'this is a test'
```

-----

### Bazeries Cipher

The Bazeries cipher, created by Etienne Bazeries, combines a transposition and a substitution with two Polybius grids, both driven by a number. The text is split into groups whose sizes are the digits of the number (repeated as needed), each group is reversed, and each letter is replaced by the letter at the same position in the second grid. The first grid holds the alphabet written in columns ; the second one is filled in rows with the number written in English words (e.g. `23` gives `TWENTY THREE`), or with an optional keyword, followed by the remaining letters.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`bazeries` | text <-> Bazeries ciphertext | `bazeries-23`, `bazeries_cipher-81257`, `bazeries-23-keyword`, `bazeries-12,3`, `bazeries-23-5-wv`, `bazeries-42-6` | Number required ; comma-separated group sizes for groups of 10 letters or more ; 5x5 grid by default, with `J` normalized to `I` (`5-XY` replaces *X* by *Y* instead) ; 6x6 grid (letters and digits, uppercase output) with `6` ; other characters and the case (5x5 grid only) are kept

```python
>>> codext.encode("DCODE", "bazeries-23")
'DLSLO'
>>> codext.decode("DLSLO", "bazeries-23")
'DCODE'
>>> codext.encode("Simple substitution plus transposition", "bazeries-81257")
'Xrmgqn brykrbkxkbkr xgqw cbrcqrweukcbw'
>>> codext.encode("DCODE", "bazeries-23-keyword")
'FMTMP'
>>> codext.encode("ATTACKATDAWNTHENRETREAT", "bazeries-12,3")
'CYOIMOSAOMMOQBMMOQWMQWC'
>>> codext.encode("Test 1234!", "bazeries-42-6")
'DTXD 2UW8!'
```

-----

### Beaufort Cipher

This is a variant of the [Vigenere Cipher](#vigenere-cipher). There is no default key, meaning that `beaufort` as the encoding scheme throws a `LookupError` indicating that the _key must be a non-empty alphabetic string_.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`beaufort` | text <-> Beaufort ciphertext | `beaufort-abcdef`, `beaufort_MySuperSecret` | key only consists of characters, not digits

```python
>>> codext.encode("This is a test !", "beaufort-abababa")
'Husj sj a hxii !'
>>> codext.encode("This is a test !", "beaufort_MySuperSecret")
'Trkc hm r zaky !'
>>> codext.decode("Husj sj a hxii !", "vigenere-abababa")
'This is a test !'
```

-----

### Bifid/Trifid Cipher

These ciphers were invented by Felix Delastelle. Each letter is replaced by its coordinates in a 5x5 Polybius square (Bifid) or in a 3x3x3 cube (Trifid). Within each block of letters, whose size is the period (the whole text by default), the coordinates are written in rows (all the rows, then all the columns, ...), then read again as groups of coordinates that give the new letters. The square or cube is filled with an optional keyword (without duplicates), then with the remaining characters of the alphabet.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`bifid` | text <-> Bifid ciphertext | `bifid-keyword`, `bifid_cipher-keyword-5`, `bifid-7`, ... | 5x5 square ; `J` is normalized to `I` ; other characters and the case are kept
`trifid` | text <-> Trifid ciphertext | `trifid-keyword`, `trifid_cipher-keyword-5`, `trifid-7`, ... | 3x3x3 cube with the 26 letters and `+` ; other characters are kept ; uppercase output (a letter can be substituted by `+`)

The codec name holds the optional keyword, then the optional period. The period only counts the letters of the alphabet.

```python
>>> codext.encode("FLEEATONCE", "bifid-bgwkzqpndsioaxefclumthyvr")
'UAEOLWRINS'
>>> codext.encode("Flee at once!", "bifid-bgwkzqpndsioaxefclumthyvr")
'Uaeo lw rins!'
>>> codext.decode("UAEOLWRINS", "bifid-bgwkzqpndsioaxefclumthyvr")
'FLEEATONCE'
>>> codext.encode("aide-toi, le ciel t'aidera", "trifid-felixmariedelastelle-5")
"FMJF-VOI, SS UFTF P'UFEQQC"
>>> codext.decode("FMJFVOISSUFTFPUFEQQC", "trifid-felixmariedelastelle-5")
'AIDETOILECIELTAIDERA'
```

-----

### Chaocipher

The Chaocipher was invented by John F. Byrne in 1918 and only disclosed in 2010. It uses two alphabets, the left one for the ciphertext and the right one for the plaintext. Each letter is replaced by the letter at the same position in the other alphabet, then both alphabets are permuted, so that the substitution changes with every letter. The alphabets are given as keywords (without duplicates) followed by the remaining letters ; by default, those of the example of [Moshe Rubin's paper](http://www.chaocipher.com/ActualChaocipher/Chaocipher-Revealing-Algorithm-Rubin.pdf) are used (`HXUCZVAMDSLKPEFJRIGTWOBNYQ` and `PTLNBQDEOYSFAVZKGJRIHWXUMC`). Other characters are kept in place, as well as the case of the letters.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`chaocipher` | text <-> Chaocipher ciphertext | `chao-cipher`, `chaocipher-left-right` | optional left and right keywords (both or none)

```python
>>> codext.encode("WELLDONEISBETTERTHANWELLSAID", "chaocipher")
'OAHQHCNYNXTSZJRRHJBYHQKSOUJY'
>>> codext.decode("OAHQHCNYNXTSZJRRHJBYHQKSOUJY", "chaocipher")
'WELLDONEISBETTERTHANWELLSAID'
>>> codext.encode("Well done, is better than well said!", "chaocipher")
'Oahq hcny, nx tszjrr hjby hqks oujy!'
```

-----

### Cisco Type 7

This implements the reversible Cisco IOS type 7 password encoding: each byte is XORed with a fixed key, starting at an offset given by the salt (from 0 to 15), and the result is the salt as two decimal digits followed by the XORed bytes in hexadecimal. Decoding reads the salt from the input.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`cisco-type7` | text <-> Cisco type 7 ciphertext | `cisco7`, `type7`, `cisco_type_7`, ... | parameterized with the salt used for encoding, e.g. `cisco-type7-8` (default: 0)

```python
>>> codext.encode("this is a test", "cisco-type7-8")
'083544471A590C04520A4C102F3830'
>>> codext.decode("0822455D0A16", "cisco-type7")
'cisco'
```

-----

### Citrix CTX1

This implements the Citrix CTX1 password encoding algorithm.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`citrix` | text <-> Citrix CTX1 ciphertext | `citrix`, `citrix-1`, `citrix_ctx1` | 

```python
>>> codext.encode("this is a test", "citrix-ctx1")
'NBBMNAAGIDEPJJBMNIFNIMEMJKEL'
>>> codext.decode("NBBMNAAGIDEPJJBMNIFNIMEMJKEL", "citrix-ctx1")
'this is a test'
```

-----

### Columnar Transposition Cipher

The text is written in rows under a keyword, then read column by column, in the alphabetical order of the keyword letters (from left to right for repeated letters). The last row may be incomplete (irregular columnar transposition) ; a regular transposition is obtained by padding the text beforehand. With a second keyword, the result is transposed again (double transposition). Every character is transposed, including whitespaces and punctuation.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`columnar` | text <-> columnar transposition ciphertext | `columnar-transposition`, `columnar-cipher` | parameterized with one or two alphanumeric keywords, e.g. `columnar-zebras` or `columnar-zebras-stripe`

```python
>>> codext.encode("WEAREDISCOVEREDFLEEATONCE", "columnar-zebras")
'EVLNACDTESEAROFODEECWIREE'
>>> codext.decode("EVLNACDTESEAROFODEECWIREE", "columnar_transposition-zebras")
'WEAREDISCOVEREDFLEEATONCE'
>>> codext.encode("WEAREDISCOVEREDFLEEATONCE", "columnar-zebras-stripe")
'CAEENSOIAEDRLEFWEDREEVTOC'
```

-----

### Enigma

The Enigma machine is the rotor cipher machine used by the German armed forces during World War II. Each letter goes through the plugboard, the rotors (from right to left), the reflector, then back through the rotors and the plugboard. The rotors step before each letter, including the double stepping of the middle rotor ; as the reflector is an involution, the same settings decrypt the ciphertext. This codec emulates the Enigma I and M3 (3 rotors among I to VIII, reflector A, B or C) and the M4 (Beta or Gamma as the fixed fourth rotor, thin reflector B or C).

The settings are given with the codec name as `enigma-[reflector]-[rotors]-[rings]-[positions]-[plugboard]`, from the left to the right of the machine, each part being optional from the right:

- *reflector*: `a`, `b`, `c`, `bthin` or `cthin` (default: `b`)
- *rotors*: their numbers (`1` to `8`), prefixed with `b` (Beta) or `g` (Gamma) for the M4 (default: `123`)
- *rings*: the ring settings, as letters (`a` for 01, `b` for 02, ... ; default: `a` for each rotor)
- *positions*: the initial positions, as letters (default: `a` for each rotor)
- *plugboard*: the pairs of swapped letters, concatenated (e.g. `avbscg` for A-V, B-S and C-G ; default: none)

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`enigma` | text <-> Enigma ciphertext | `enigma`, `enigma_cipher-c-678`, `enigma-b-245-bul-bla-avbscgdlfuhzinkmowrx`, `enigma-cthin-b568-epel-cdsz-aebfcmdqhujnlxprszvw` | Only ASCII letters are encrypted (their case is kept) ; other characters are left unchanged and do not step the rotors

```python
>>> codext.encode("Attack at dawn", "enigma")
'Bzhgno cr rtcm'
>>> codext.decode("Bzhgno cr rtcm", "enigma")
'Attack at dawn'
>>> codext.encode("Attack at dawn", "enigma-b-245-bul-bla-avbscgdlfuhzinkmowrx")
'Evhqzv rr blri'
>>> codext.encode("Attack at dawn", "enigma-cthin-b568-epel-cdsz-aebfcmdqhujnlxprszvw")
'Svbyeg oi nxcm'
```

-----

### ESAB-46

This toy cipher ("Base-64" reversed) comes from online JavaScript encryption tools. Like [ATOM-128](#atom-128), it is Base64 with a shuffled alphabet, whose 65th character (`/`) is used for padding, and the text is first escaped with JavaScript's `escape()`, then unescaped after decoding.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`esab46` | text <-> ESAB-46 ciphertext | `esab-46`, `esb46`, `esb_46` | 

```python
>>> codext.encode("this is a test", "esab46")
'9sRZ8i0ivsVj6z5gLy0iv4xV8nw/'
>>> codext.decode("9sRZ8i0ivsVj6z5gLy0iv4xV8nw/", "esab-46")
'this is a test'
```

-----

### EZIP-64

This toy cipher, a variant of [ARMON-64](#armon-64), comes from online JavaScript encryption tools. It works the same way, but with blocks of a third of the key length (rounded), a factor of 0.02 in its fourth operation and `/` as the separator.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`ezip64` | text <-> EZIP-64 ciphertext | `ezip-64`, `ezip_64` | parameterized with a mandatory key of at least 3 characters, e.g. `ezip64-secret` ; only characters with a code below 256

!!! warning "Precision"

    As the computations are done with double-precision floats, as in JavaScript, keys of more than 19 characters give blocks that are too large to be decrypted exactly.

```python
>>> codext.encode("test", "ezip64-test")
'-261.47089108910893/-261.81544554455445/-261.4938613861386/-261.47089108910893'
>>> codext.decode("-261.47089108910893/-261.81544554455445", "ezip64-test")
'te'
```

-----

### FERON-74

This toy cipher comes from online JavaScript encryption tools. Like [ATOM-128](#atom-128), it is Base64 with a shuffled alphabet, whose 65th character (`4`) is used for padding, and the text is first escaped with JavaScript's `escape()`, then unescaped after decoding.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`feron74` | text <-> FERON-74 ciphertext | `feron-74`, `feron_74` | 

```python
>>> codext.encode("this is a test", "feron74")
'sbxMC161WbyZ/rSiNq61WcDyCnA4'
>>> codext.decode("sbxMC161WbyZ/rSiNq61WcDyCnA4", "feron-74")
'this is a test'
```

-----

### Four-square Cipher

The Four-square cipher, invented by Felix Delastelle, substitutes pairs of letters using four squares arranged in a 2x2 matrix: the upper-left and lower-right ones hold the alphabet in order, while the upper-right and lower-left ones are filled with two keywords. The first letter of each pair is located in the upper-left square and the second one in the lower-right square ; they are replaced by the letters at the other corners of the rectangle they form (in the upper-right square, then in the lower-left one).

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`foursquare` | text <-> Four-square ciphertext | `four-square-example-keyword`, `foursquare_cipher-key1-key2`, `foursquare-example-keyword-5-qk`, `foursquare-secret-key-6` | Two keywords required ; 5x5 squares by default, with `J` normalized to `I` (`5-XY` replaces *X* by *Y* instead) ; 6x6 squares (letters and digits) with `6` ; whitespace removed, uppercase output, padded with `X` to an even number of letters

```python
>>> codext.encode("help me obi wan kenobi", "foursquare-example-keyword")
'FYNFNEHWBXAFFOKHMD'
>>> codext.decode("FYNFNEHWBXAFFOKHMD", "foursquare-example-keyword")
'HELPMEOBIWANKENOBI'
>>> codext.encode("help me obi wan kenobi", "foursquare-example-keyword-5-qk")
'FYGMKYHOBXMFKKKIMD'
>>> codext.encode("Hide the gold 2026", "foursquare-secret-key-6")
'FFTAQFSIOGT1209T'
```

-----

### Fractionated Morse Cipher

The text is converted to Morse code, with "x" between the characters, "xx" between the words and a trailing "xx". This Morse string is split into groups of three symbols (the last one being padded with dots), and each group is replaced by a letter of an alphabet ordered with an optional keyword. Case and whitespace are not kept.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`fractionated-morse` | text <-> fractionated Morse ciphertext | `fmorse`, `fractionated_morse`, ... | parameterized with an optional keyword, e.g. `fractionated-morse-roundtable`

```python
>>> codext.encode("this is a test", "fractionated-morse")
'PASSICAYRPSHY'
>>> codext.encode("this is a test", "fractionated-morse-roundtable")
'JRPPLURYMJPBY'
>>> codext.decode("JRPPLURYMJPBY", "fmorse-roundtable")
'this is a test'
```

-----

### GILA7

This toy cipher comes from online JavaScript encryption tools. Like [ATOM-128](#atom-128), it is Base64 with a shuffled alphabet, whose 65th character (`G`) is used for padding, and the text is first escaped with JavaScript's `escape()`, then unescaped after decoding.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`gila7` | text <-> GILA7 ciphertext | `gila-7`, `gila_7` | 

```python
>>> codext.encode("this is a test", "gila7")
'3+1QqbzbB+Odcg=5v0zbBWfOqxyG'
>>> codext.decode("3+1QqbzbB+Odcg=5v0zbBWfOqxyG", "gila-7")
'this is a test'
```

-----

### Gronsfeld Cipher

This is a variant of the [Vigenere Cipher](#vigenere-cipher) whose key is made of digits, each digit giving the shift of a letter (0 to 9). There is no default key, meaning that `gronsfeld` as the encoding scheme throws a `LookupError` indicating that the _key must be a non-empty numeric string_.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`gronsfeld` | text <-> Gronsfeld ciphertext | `gronsfeld-31415`, `gronsfeld_cipher-0123` | key only consists of digits

```python
>>> codext.encode("ATTACKATDAWN", "gronsfeld-31415")
'DUXBHNBXEFZO'
>>> codext.decode("DUXBHNBXEFZO", "gronsfeld-31415")
'ATTACKATDAWN'
```

-----

### Hill Cipher

The letters (A=0, ..., Z=25) are taken in blocks of n, each block being multiplied (as a column vector) by a n x n key matrix modulo 26. The key matrix is given as a keyword whose length is a square (4 letters for a 2x2 matrix, 9 for a 3x3 matrix, ...), filled row by row ; it must be invertible modulo 26, that is, its determinant must be coprime with 26. Other characters are kept in place, as well as the case of the letters. When encoding, the last block is padded with "`X`", the padding letters being appended to the text.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`hill` | text <-> Hill ciphertext | `hill-ddcf`, `hill_cipher-gybnqkurp` | key length must be a square and the key matrix must be invertible modulo 26

```python
>>> codext.encode("ACT", "hill-gybnqkurp")
'POH'
>>> codext.decode("POH", "hill-gybnqkurp")
'ACT'
>>> codext.encode("Cats!", "hill-gybnqkurp")
'Finh!AE'
```

-----

### Nihilist Cipher

Each letter of the text and of the key is replaced by its coordinates (row and column, from 1 to 5) in a 5x5 Polybius square (I and J sharing a cell), read as a two-digit number. The ciphertext is made of the sums of the numbers of the text and of the repeated key, separated by spaces. The square is filled with an optional keyword (without duplicates), then with the remaining letters of the alphabet. When encoding, whitespaces are ignored ; when decoding, the numbers are separated by whitespaces.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`nihilist` | text <-> Nihilist ciphertext | `nihilist-russian`, `nihilist_cipher-zebras-russian` | parameterized with an optional square keyword and a key

```python
>>> codext.encode("DYNAMITE WINTER PALACE", "nihilist-zebras-russian")
'37 106 62 36 67 47 86 26 104 53 62 77 27 55 57 66 55 36 54 27'
>>> codext.decode("37 106 62 36 67 47 86 26 104 53 62 77 27 55 57 66 55 36 54 27", "nihilist-zebras-russian")
'DYNAMITEWINTERPALACE'
>>> codext.encode("Hello", "nihilist-key")
'48 30 85 56 49'
```

-----

### Phillips Cipher

This implements Phillips cipher, a polyalphabetic code using 8 grids generated with one keyword.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`phillips` | text <-> phillips ciphertext | `phillips-key`, `phillips_password`, ... |

```python
>>> codext.encode("this is a test", "phillips_mysuperkey")
'ZCNM NM E XKMVZ'
>>> codext.encode("Another Test String", "phillips-PaSsWoRd")
'SMEZKBE LBON OLEHQHV'
>>> codext.decode("SMEZKBE LBON OLEHQHV", "phillips-password")
'ANOTHER TEST STRINGX'
```

-----

### Polybius Square Cipher

This implements the well-known Polybius Square cipher, using the square with the alphabet in normal order as the default. It can be used dynamically with a custom alphabet.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`polybius` | text <-> polybius square ciphertext | `polybius-square`, `polybius_BACDEFGHIKLMNOPQRSTUVWXYZ`, ... |

```python
>>> codext.encode("this is a test", "polybius")
'44232443 2443 11 44154344'
>>> codext.encode("this is a test", "polybius_BACDEFGHIKLMNOPQRSTUVWXYZ")
'44232443 2443 12 44154344'
>>> codext.decode("44232443 2443 11 441543445", "polybius-square", errors="replace")
'THIS IS A TEST?'
```

-----

### Porta Cipher

This is a variant of the [Vigenere Cipher](#vigenere-cipher) where each pair of key letters (AB, CD, ..., YZ) selects one of 13 reciprocal alphabets swapping the halves A-M and N-Z. Hence, decoding is the same as encoding. There is no default key, meaning that `porta` as the encoding scheme throws a `LookupError` indicating that the _key must be a non-empty alphabetic string_.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`porta` | text <-> Porta ciphertext | `porta-abcdef`, `porta_cipher-MySuperSecret` | key only consists of characters, not digits

```python
>>> codext.encode("DEFENDTHEEASTWALLOFTHECASTLE", "porta-fortification")
'SYNNJSCVRNRLAHUTUKUCVRYRLANY'
>>> codext.decode("SYNNJSCVRNRLAHUTUKUCVRYRLANY", "porta-fortification")
'DEFENDTHEEASTWALLOFTHECASTLE'
```

-----

### Rail Fence Cipher

This implements the Rail Fence encoding algorithm, using 3 rails and offset 0 as the default parameters. The encoding fence is built from the top ; the `up` flag can be used to build the fence from the bottom. Note that trying parameters that do not fit the input length will trigger a `ValueError` mentioning the bad value.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`rail` | text <-> rail fence ciphertext, X rails and Y offset | `rail-X-Y`, `rail_X_Y`, `rail-X-Y-up`, `zigzag`, ... | 

```python
>>> codext.encode("this is a test", "zigzag")
't ashsi  etist'
>>> codext.encode("this is a test", "rail-5-3")
'it sss etiath '
>>> codext.decode("it sss etiath ", "zigzag_5-3")
'this is a test'
```

-----
### ROT N

This is a dynamic encoding, that is, it can be called with an integer to define the ROT offset. Encoding will apply a positive offset, decoding will apply a negative one.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`rot` | text <-> rot(1) ciphertext | `rot1`, `rot-1`, `rot_25`, `caesar13` | Dynamic ROT parameter ; belongs to [1, 26[
`rot47` | text <-> rot47 ciphertext |  | 

```python
>>> codext.encode("this is a test", "rot-15")
'iwxh xh p ithi'
>>> codext.encode("iwxh xh p ithi", "rot20")
'cqrb rb j cnbc'
>>> codext.decode("cqrb rb j cnbc", "rot_9")
'this is a test'
```

-----

### Shift

This is a dynamic encoding, that is, it can be called with an integer to define the shift offset. Encoding will apply a positive offset, decoding will apply a negative one.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`shift` | text <-> shift(1) ciphertext | `shift1`, `shift-158`, `shift_255` | Dynamic shift parameter ; belongs to [1, 256[

```python
>>> codext.encode("this is a test", "shift-3")
'wklv#lv#d#whvw'
>>> codext.decode("wklv#lv#d#whvw", "shift10")
'mabl\x19bl\x19Z\x19m^lm'
>>> codext.encode("mabl\x19bl\x19Z\x19m^lm", "ordshift_7")
'this is a test'
```

-----

### Playfair Cipher

The Playfair cipher is a symmetric encryption method using polygram substitution with bigrams (pairs of letters), invented in 1854 by Charles Wheatstone, but popularized by Lord Playfair.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`playfair` | text <-> Playfair ciphertext | `playfair`, `playfair-playfairexample`, `playfair-keyword` | Dynamic key parameter ; letters only ; `J` is normalized to `I`

```python
>>> codext.encode("HIDETHEGOLDINTHETREESTUMP", "playfair-playfairexample")
'BMODZBXDNABEKUDMUIXMMOUVIF'
>>> codext.decode("BMODZBXDNABEKUDMUIXMMOUVIF", "playfair-playfairexample")
'HIDETHEGOLDINTHETREXESTUMP'
>>> codext.decode(codext.encode("INSTRUMENT", "playfair-keyword"), "playfair-keyword")
'INSTRUMENT'
```

-----

### Skip Cipher

This transposition cipher reads the text by jumping a constant number of characters each time, starting from a given position (1 by default) and looping on the text. The skip value must be coprime with the length of the text, otherwise some characters would never be read (an error is then raised, or the text is left unchanged with `errors="leave"`). Every character is transposed, including whitespaces and punctuation ; remove them beforehand to get the classical form.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`skip` | text <-> Skip ciphertext | `skip-3`, `skip_cipher-3-2` | parameterized with the skip value and an optional start position (from 1)

```python
>>> codext.encode("DCODE", "skip-3")
'DDCEO'
>>> codext.decode("DDCEO", "skip-3")
'DCODE'
>>> codext.encode("DCODE", "skip-3-2")
'CEODD'
```

-----

### Trithemius Cipher

This is a variant of the [Vigenere Cipher](#vigenere-cipher) with key `"ABCDEFGHIJKLMNOPQRSTUVWXYZ"`.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`trithemius` | text <-> Trithemius ciphertext | `trithemius`, `trithemius_cipher` | 

```python
>>> codext.encode("This is a test !", "trithemius")
'Tikv mx g ambd !'
>>> codext.decode("Tikv mx g ambd !", "trithemius")
'This is a test !'
```

-----

### Two-square Cipher

The Two-square cipher (or Double Playfair), invented by Charles Wheatstone, substitutes pairs of letters using two squares filled with two keywords, placed one above the other (vertical, by default) or side by side (horizontal). The first letter of each pair is located in the first square and the second one in the second square ; they are replaced by the letters at the other corners of the rectangle they form. In the vertical variant, the output starts with the letter of the upper square and a pair whose letters share a column is left unchanged ; in the horizontal one, the output starts with the letter of the right square and a pair whose letters share a row is reversed.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`twosquare` | text <-> Two-square ciphertext | `two-square-example-keyword`, `double-playfair-key1-key2`, `twosquare-key-word-h`, `twosquare-key-word-horizontal-5-qk`, `twosquare-secret-key-v-6` | Two keywords required ; vertical (`v`, by default) or horizontal (`h`) ; 5x5 squares by default, with `J` normalized to `I` (`5-XY` replaces *X* by *Y* instead) ; 6x6 squares (letters and digits) with `6` ; whitespace removed, uppercase output, padded with `X` to an even number of letters

```python
>>> codext.encode("help me obi wan kenobi", "twosquare-example-keyword")
'HECMXWSRKYXPHWNODG'
>>> codext.encode("help me obi wan kenobi", "twosquare-example-keyword-5-qk")
'HEDLXWSDJYANHOTKDG'
>>> codext.encode("DCODEZ", "twosquare-key-word-h")
'CDLBAV'
>>> codext.decode("CDLBAV", "twosquare-key-word-h")
'DCODEZ'
```

-----

### VIC Cipher

The VIC cipher combines a straddling checkerboard substitution (converting letters to a stream of digits) and an over-encryption based on a modulo-10 sum with eventually a conversion from digits to text.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`vic` | text <-> VIC digit/text ciphertext | `vic-keyword`, `vic-key-12`, `vic-^-26-0248`, `vic-*-73-534T` | optional checkerboard keyword or alphabet marker, blank positions (exactly 2 distinct digits), over-encryption key (digits), "`T`" marker for text conversion

Alphabet markers:
- `*`: uses "`ABC[...]XYZ./`" (uppercase letters + "`./`")
- `^`: uses "`./ZYX[...]CBA`" ("`./`" + reversed uppercase letters)

```python
>>> import codext
>>> codext.encode("VICTOR", "vic-^-26-0248T")
'VVXYWYY.XYJ'
>>> codext.decode("VVXYWYY.XYJ", "vic-^-26-0248T")
'VICTOR2'  # trailing superfluous letter because of text conversion
>>> codext.encode("LONGTESTSTRING", "vic-^-85-72564")
'5031237844273727064454072378'
```

-----

### Vigenere Cipher

This is a dynamic encoding, that is, it holds the key. There is no default key, meaning that `vigenere` as the encoding scheme throws a `LookupError` indicating that the _key must be a non-empty alphabetic string_.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`vigenere` | text <-> Vigenere ciphertext | `vigenere-abcdef`, `vigenere_MySuperSecret` | key only consists of characters, not digits

```python
>>> codext.encode("This is a test !", "vigenere-abababa")
'Tiit it a tfsu !'
>>> codext.encode("This is a test !", "vigenere_MySuperSecret")
'Ffam xw r liuk !'
>>> codext.decode("Tiit it a tfsu !", "vigenere-abababa")
'This is a test !'
```

-----

### XOR with 1 byte

This is a dynamic encoding, that is, it can be called with an integer to define the ordinal of the byte to XOR with the input text.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`xor` | text <-> XOR(1) ciphertext | `XOR1`, `xor22`, `xor-158`, `xor_255` | Dynamic XOR parameter ; belongs to [1, 256[

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
