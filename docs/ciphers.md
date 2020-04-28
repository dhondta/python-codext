`codext` also implements several simple cryptographic ciphers that are comparable to encodings for each value of their keys as these are too weak.

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

### Affine Cipher

This codec implements the Affine monoalphabetic substitution cipher. It is parametrizable with a mask for generating the alphabet and the parameters `a` and `b`. By default, it uses mask "`lus`" and parameters `a=1` and `b=2` but it can be set as in the examples hereafter.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`affine` | Affine <-> text | `affine` (uses default mask "`?l?u?s`" with `a=1` and `b=2`), `affine_cipher-?l?u?d?s-5,8`, `affine- .,?!?u?d-23,6`, ...

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

### Atbash Cipher

It implements the monoalphabetic substitution cipher used for the Hebrew alphabet. By default, it considers the lowercase and uppercase letters and the whitespace for the alphabet. It can also use a mask to extend it.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`atbash` | Atbash <-> text | `atbash` (uses default mask "`lus`"), `atbash_cipher-?l?d?s`, ...

```python
>>> codext.encode("this is a test", "atbash")
'HTSIaSIa aHWIH'
>>> codext.encode("this is a test", "atbash-?l?u?p?s")
'.^]/a]/a a.{/.'
>>> codext.decode(".^]/a]/a a.{/.", "atbash_cipher_?l?u?p?s")
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
