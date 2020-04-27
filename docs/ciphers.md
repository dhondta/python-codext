`codext` also implements several simple cryptographic ciphers that are comparable to encodings for each value of their keys as these are too weak.

-----

### Atbash Cipher

It implements the monoalphabetic substitution cipher used for the Hebrew alphabet.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`atbash` | Atbash <-> text | `atbash`, `atbash_cipher`

```python
>>> codext.encode("this is a test", "atbash")
'GSRH RH Z GVHG'
>>> codext.decode('GSRH RH Z GVHG', "atbash")
'this is a test'
```

-----

### Baconian Cipher

It support only letters.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`bacon` | Bacon <-> text | `bacon-cipher`, `baconian_cipher`, `bacon-01`, `bacon-10` | Dynamic tokens mapping ; we can define a mapping of encoding's tokens (original tokens: `ab`)

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
`barbie` | Barbie <-> text | `barbie-1`, `barbie-2`, `barbie-3`, `barbie-4`

```python
>>> codext.encode("this is a test", "barbie-1")
'hstf tf i hafh'
>>> codext.encode("this is a test", "barbie_3")
'fpsu su h ftuf'
>>> codext.decode("fpsu su h ftuf", "barbie-3")
'this is a test'
```

-----

### ROT N

This is a dynamic encoding, that is, it can be called with an integer to define the ROT offset. Encoding will apply a positive offset, decoding will apply a negative one.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`rotN` | ROT(1) <-> text | `rot1`, `rot-1`, `rot_1` | 
`rotN` | ROT(X) <-> text | ... | 
`rotN` | ROT(25) <-> text | `rot25`, `rot-25`, `rot_25` | 

```python
>>> codext.encode("this is a test", "rot-15")
'iwxh xh p ithi'
>>> codext.encode("iwxh xh p ithi", "rot20")
'cqrb rb j cnbc'
>>> codext.decode("cqrb rb j cnbc", "rot_9")
'this is a test'
```

-----

### XOR with 1 byte

This is a dynamic encoding, that is, it can be called with an integer to define the ordinal of the byte to XOR with the input text.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`xorN` | XOR(1) <-> text | `XOR1`, `xor1`, `xor-1`, `xor_1` | 
`xorN` | XOR(X) <-> text | ... | 
`xorN` | XOR(255) <-> text | `XOR255`, `xor255`, `xor-255`, `xor_255` | 

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
