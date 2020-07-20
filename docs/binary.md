With `codext`, the `codecs` library has multiple new encodings in addition to [the native ones](https://docs.python.org/3.8/library/codecs.html#standard-encodings), like presented hereafter.

Unless explicitely specified, each codec supports writing to and reading from a file.

!!! warning "Lossy conversion"
    
    Some encodings are lossy, meaning that it is not always possible to decode back to the exact start string. This should be considered especially when chaining codecs.

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

### Excess-3

Also called *Stibitz code*, it converts letters to ordinals, left-pads with zeros and then applies Excess-3 (Stibitz) code to get groups of 4 bits that are finally reassembled into bytes.

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

