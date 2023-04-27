`codext` also provides some very common encodings, for the sake of simplicity (e.g. while chaining codecs with [the CLI tool](../cli.html)).

-----

### A1Z26

This simple codec converts letters to their order number in the alphabet using a separator between characters and keeping words separated by a whitespace. It is similar to the [`consonant-vowel-indices`](others.html#letter-indices) encoding.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`a1z26` | text <-> alphabet order numbers | `a1z26`, `a1z26-/`, `a1z26-,`, ... | this codec does not preserve the case and is dynamic (separator of characters in each word can be customized among these: "`-_/|,;:*`")

```python
>>> codext.encode("This is a test", "a1z26")
'20-8-9-19 9-19 1 20-5-19-20'
>>> codext.decode("20-8-9-19 9-19 1 20-5-19-20", "a1z26")
'this is a test'
```

-----

### Octal

This simple codec converts characters into their octal values.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`octal` | text <-> octal digits | `octals` | groups of 3-chars octal values when encoded
`octal-spaced` | text <-> spaced octal digits | `octals-spaced` | whitespace-separated suite of variable-length groups of octal digits when encoded

```python
>>> codext.encode("this is a test", "octal")
'164150151163040151163040141040164145163164'
>>> codext.decode("164150151163040151163040141040164145163164", "octals")
'this is a test'
```

```python
>>> codext.encode("this is a test", "octal-spaced")
'164 150 151 163 40 151 163 40 141 40 164 145 163 164'
>>> codext.decode("164 150 151 163 40 151 163 40 141 40 164 145 163 164", "octals-spaced")
'this is a test'
```

-----

### Ordinal

This simple codec converts characters into their ordinals.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`ordinal` | text <-> ordinal digits | `ordinals` | groups of 3-chars ordinal values when encoded
`ordinal-spaced` | text <-> spaced ordinal digits | `ordinals-spaced` | whitespace-separated suite of variable-length groups of ordinal digits when encoded

```python
>>> codext.encode("this is a test", "ordinal")
'116104105115032105115032097032116101115116'
>>> codext.decode("116104105115032105115032097032116101115116", "ordinals")
'this is a test'
```

```python
>>> codext.encode("this is a test", "ordinal-spaced")
'116 104 105 115 32 105 115 32 97 32 116 101 115 116'
>>> codext.decode("116 104 105 115 32 105 115 32 97 32 116 101 115 116", "ordinals-spaced")
'this is a test'
```

