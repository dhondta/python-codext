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

