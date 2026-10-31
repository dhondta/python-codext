`codext` also adds common binary encodings. For instance, the Manchester code, that encodes digits, is applied to the ordinals of the input text and the resulting binary stream is converted back to characters.

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

### Binary Coded Decimal (BCD)

It converts characters to their odrinals, left-pads with zeros, converts digits to 4-bits groups and then make characters with the assembled groups. It can also use a 4-bits prefix for making new characters. It then allows to define extended versions of BCD.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`bcd` | text <-> BCD encoded text | `binary_coded_decimals` | 
`bcd-extended0` | text <-> BCD encoded text using prefix `0000` | `bcd_ext0`, `bcd-extended-zeros`, `binary_coded_decimals_extended_0` | 
`bcd-extended1` | text <-> BCD encoded text using prefix `1111` | `bcd_ext1`, `bcd-extended-ones`, `binary_coded_decimals_extended_1` | 

```python
>>> codext.encode("Test", "bcd")
'\x08A\x01\x11Q\x16'
>>> codext.decode("\x08A\x01\x11Q\x16", "binary_coded_decimal")
'Test'
>>> codext.encode("Test", "bcd_ext_zero")
'\x00\x08\x04\x01\x00\x01\x01\x01\x05\x01\x01\x06\x00'
>>> codext.decode("\x00\x08\x04\x01\x00\x01\x01\x01\x05\x01\x01\x06\x00", "bcd-ext0")
'Test'
>>> codext.encode("Test", "bcd_extended_ones")
'\xf0\xf8\xf4\xf1\xf0\xf1\xf1\xf1\xf5\xf1\xf1\xf6\xf0'
>>> codext.decode("\xf0\xf8\xf4\xf1\xf0\xf1\xf1\xf1\xf5\xf1\xf1\xf6\xf0", "bcd_ext1")
'Test'
```

-----

### Chuck Norris Unary

Each character is written with the 7 bits of its ASCII code, then the resulting bit string is cut into runs of identical bits, each run being written as two blocks of zeros separated by a space: `0` for a run of 1s or `00` for a run of 0s, followed by as many zeros as bits in the run (see the [CodinGame puzzle](https://www.codingame.com/training/easy/chuck-norris)). Only ASCII characters can be encoded.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`chuck-norris` | text <-> Chuck Norris unary code | `chucknorris`, `chuck-norris-unary`, `chuck_norris_code` | ASCII characters only

```python
>>> codext.encode("CC", "chuck-norris")
'0 0 00 0000 0 000 00 0000 0 00'
>>> codext.decode("0 0 00 0000 0 000 00 0000 0 00", "chuck-norris")
'CC'
```

-----

### Elias Gamma/Delta Codes

These universal codes write positive integers as self-delimiting codewords, hence concatenated without separator:

- Elias gamma: N zeros followed by the N+1 bits of the integer
- Elias delta: the Elias gamma codeword of the number of bits of the integer, followed by its bits without the leading 1

Each character of the text is encoded from its ordinal + 1 (as 0 cannot be encoded), the output being a string of bits ; when decoding, the whitespaces are ignored. With the `-integers` variant (or `-int`), the text holds integers (from 1) in decimal, separated by whitespaces or commas, and the decoded integers are separated by a space.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`elias-gamma` | text <-> Elias gamma bits | `gamma`, `eliasgamma`, `elias-gamma-int` | `-int(egers)` for lists of integers
`elias-delta` | text <-> Elias delta bits | `delta`, `eliasdelta`, `elias-delta-int` | `-int(egers)` for lists of integers

```python
>>> codext.encode("Hi!", "elias-gamma")
'0000001001001000000110101000000100010'
>>> codext.encode("Hi!", "elias-delta")
'00111001001001111010100011000010'
>>> codext.decode("00111001001001111010100011000010", "delta")
'Hi!'
>>> codext.encode("1 2 3 17", "elias-gamma-int")
'1010011000010001'
```

-----

### Excess-3

Also called *Stibitz code*, it converts characters to ordinals, left-pads with zeros and then applies Excess-3 (Stibitz) code to get groups of 4 bits that are finally reassembled into bytes.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`excess3` | text <-> XS3 encoded text | `excess-3`, `xs3`, `stibitz` | 

```python
>>> codext.encode("This is a test!", "excess-3")
';t7C\x84H6T8D\x83e<£eD\x944D\x84I6`'
>>> codext.decode(";t7C\x84H6T8D\x83e<£eD\x944D\x84I6`", "stibitz")
'This is a test!'
```

-----

### Fibonacci Code

This universal code writes positive integers as self-delimiting codewords, hence concatenated without separator: the Zeckendorf representation of the integer (sum of non-consecutive Fibonacci numbers 1, 2, 3, 5, 8, ...), from the least significant term, followed by an additional 1 (each codeword ends with `11`).

Each character of the text is encoded from its ordinal + 1 (as 0 cannot be encoded), the output being a string of bits ; when decoding, the whitespaces are ignored. With the `-integers` variant (or `-int`), the text holds integers (from 1) in decimal, separated by whitespaces or commas, and the decoded integers are separated by a space.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`fibonacci` | text <-> Fibonacci code bits | `fib`, `fibonacci-coding`, `fibonacci-int` | `-int(egers)` for lists of integers

```python
>>> codext.encode("Hi!", "fibonacci")
'000101001110100100011000000011'
>>> codext.decode("000101001110100100011000000011", "fibonacci")
'Hi!'
>>> codext.encode("1 2 3 17", "fibonacci-int")
'1101100111010011'
>>> codext.decode("1101100111010011", "fibonacci-integers")
'1 2 3 17'
```

-----

### Gray

Also called *reflected binary code*, it implements the Gray code applied to characters while converted to bytes.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`gray` | text <-> gray encoded text | `reflected-bin`, `reflected_binary` | 

```python
>>> codext.encode("this is a test", "gray")
'N\\]J0]J0Q0NWJN'
>>> codext.decode("N\\]J0]J0Q0NWJN", "gray")
'this is a test'
>>> codext.encode("THIS IS A TEST", "gray")
'~lmz0mz0a0~gz~'
>>> codext.decode("~lmz0mz0a0~gz~", "gray")
'THIS IS A TEST'
```

-----

### Hamming

The [Hamming(7,4)](https://en.wikipedia.org/wiki/Hamming(7,4)) code, invented by Richard Hamming in 1950, writes 4 data bits with 3 parity bits, as the codeword `p1 p2 d1 p3 d2 d3 d4`, where `p1 = d1 ^ d2 ^ d4`, `p2 = d1 ^ d3 ^ d4` and `p3 = d2 ^ d3 ^ d4`: the parity checks of a received codeword give the position of a flipped bit, hence a single-bit error is corrected. The extended Hamming(8,4) code (aka SECDED) adds an overall parity bit, so that two flipped bits are detected instead of being wrongly corrected. Each half of a byte is encoded as a codeword in a byte (whose most significant bit is the overall parity bit with Hamming(8,4) and 0 with Hamming(7,4)), hence each input byte gives two output bytes.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`hamming` | data <-> Hamming(7,4) codewords | `hamming74`, `hamming-7-4` | single-bit errors silently corrected (two flipped bits in a codeword are wrongly corrected)
`hamming84` | data <-> Hamming(8,4) codewords | `hamming-8-4`, `secded` | single-bit errors silently corrected ; double-bit errors (and a trailing byte) only replaced, dropped or left with a non-strict errors handling

```python
>>> codext.encode(b"Hi", "hamming84")
b'\xcc\xf0f\x99'
>>> codext.decode(b"\xc8\xf0f\x99", "hamming84")  # with a flipped bit in the first codeword
b'Hi'
>>> codext.decode(b"\x03\xc3", "hamming84", "replace")  # with two flipped bits in the first codeword
b'?'
```

-----

### Manchester

This codec XORes each group of 4 bits of the input text with a 1-byte clock signal, e.g. `0x55` giving in binary `01010101`.

[Differential Manchester](https://en.wikipedia.org/wiki/Differential_Manchester_encoding) code also has a transition in the middle of each bit period, but writes the bits as the presence or absence of a transition at the start of their period, hence it does not depend on the polarity of the signal: by default, 0 is written with a transition at the start and 1 without (as with IEEE 802.5, Token Ring), while the inverted variant writes 1 with a transition. The level starts low and each input byte gives two output bytes.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`manchester` | text <-> manchester encoded text | | clock signal is `0x55` (`01010101`)
`manchester-inverted` | text <-> manchester encoded text | `ethernet`, `ieee802.4` | clock signal is `0xaa` (`10101010`)
`differential-manchester` | text <-> differential manchester encoded text | `diff-manchester`, `ieee802.5` | 0 written with a transition at the start of its period ; missing transitions in the middle of the periods only accepted with a non-strict errors handling
`differential-manchester-inverted` | text <-> differential manchester encoded text | `diff-manchester-inverted` | 1 written with a transition at the start of its period

```python
>>> codext.encode("This is a test!", "manchester")
'fei\x95i\x96jZYUi\x96jZYUiVYUjeifjZjeYV'
>>> codext.decode("fei\x95i\x96jZYUi\x96jZYUiVYUjeifjZjeYV", "manchester")
'This is a test!'
>>> codext.encode("This is a test!", "manchester-inverted")
'\x99\x9a\x96j\x96i\x95¥¦ª\x96i\x95¥¦ª\x96©¦ª\x95\x9a\x96\x99\x95¥\x95\x9a¦©'
>>> codext.decode("\x99\x9a\x96j\x96i\x95¥¦ª\x96i\x95¥¦ª\x96©¦ª\x95\x9a\x96\x99\x95¥\x95\x9a¦©", "ethernet")
'This is a test!'
>>> codext.encode(b"A", "differential-manchester")
b'\x95V'
>>> codext.decode(b"\x95V", "differential-manchester")
b'A'
```

-----

### NRZI

[Non-Return-to-Zero Inverted](https://en.wikipedia.org/wiki/Non-return-to-zero#NRZI) (NRZI) is a line code where each bit gives the level of the signal during its period, a bit being written as a change of the level (a transition) or as no change, hence it does not depend on the polarity of the signal. By default, the convention NRZ-M ("mark") is used: 1 is written with a transition and 0 without, while the `-space` variant uses the convention NRZ-S, where 0 is written with a transition (as used e.g. by USB and HDLC, before their bit stuffing). The level starts low and each input byte gives an output byte.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`nrzi` | text <-> NRZI encoded text | `nrz-i`, `nrz-m`, `nrzi-mark` | 1 written with a transition
`nrzi-space` | text <-> NRZI encoded text | `nrz-s` | 0 written with a transition

```python
>>> codext.encode(b"\xb2", "nrzi")
b'\xdc'
>>> codext.encode(b"\xb2", "nrzi-space")
b'v'
>>> codext.decode(b"\xdc", "nrzi")
b'\xb2'
```

-----

### Rotate N bits

This codec rotates of N bits each byte of an input string.

!!! note "Lossless"
    
    This codec does not use the "`<<`" and "`>>`" operators as it is lossy in some cases. Instead, it rotates per group of 8 bits.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`rotate` | text <-> N-bits-rotated text | `rotate-N`, `rotate_bits-N`, `rotate-right-N`, `rotate_left_N` | N belongs to [1,7] ; when nothing specified, it rotates to the right

```python
>>> codext.encode("test", "rotate-1")
':29:'
>>> codext.encode("test", "rotatebits-1")
':29:'
>>> codext.encode("test", "rotate_right-1")
':29:'
>>> codext.encode("test", "rotate_left_1")
'èÊæè'
```

