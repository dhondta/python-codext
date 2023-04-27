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

### Manchester

This codec XORes each group of 4 bits of the input text with a 1-byte clock signal, e.g. `0x55` giving in binary `01010101`.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`manchester` | text <-> manchester encoded text | | clock signal is `0x55` (`01010101`)
`manchester-inverted` | text <-> manchester encoded text | `ethernet`, `ieee802.4` | clock signal is `0xaa` (`10101010`)

```python
>>> codext.encode("This is a test!", "manchester")
'fei\x95i\x96jZYUi\x96jZYUiVYUjeifjZjeYV'
>>> codext.decode("fei\x95i\x96jZYUi\x96jZYUiVYUjeifjZjeYV", "manchester")
'This is a test!'
>>> codext.encode("This is a test!", "manchester-inverted")
'\x99\x9a\x96j\x96i\x95¥¦ª\x96i\x95¥¦ª\x96©¦ª\x95\x9a\x96\x99\x95¥\x95\x9a¦©'
>>> codext.decode("\x99\x9a\x96j\x96i\x95¥¦ª\x96i\x95¥¦ª\x96©¦ª\x95\x9a\x96\x99\x95¥\x95\x9a¦©", "ethernet")
'This is a test!'
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

