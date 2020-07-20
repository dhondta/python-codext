With `codext`, the `codecs` library has multiple new encodings in addition to [the native ones](https://docs.python.org/3.8/library/codecs.html#standard-encodings), like presented hereafter.

Unless explicitely specified, each codec supports writing to and reading from a file.

!!! warning "Lossy conversion"
    
    Some encodings are lossy, meaning that it is not always possible to decode back to the exact start string. This should be considered especially when chaining codecs.

-----

### Resistor Color Codes

This uses the [electronic color code](https://en.wikipedia.org/wiki/Electronic_color_code#Resistor_color-coding) to encode digits, displaying colors in the terminal with ANSI color codes.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`resistor` | text <-> resistor colors | `resistors-color`, `resistor_color_code` | visually, it only works in a terminal supporting ANSI color codes

```python
>>> codext.encode("1234", "resistor")
'\x1b[48;5;130m \x1b[0;00m\x1b[48;5;1m \x1b[0;00m\x1b[48;5;214m \x1b[0;00m\x1b[48;5;11m \x1b[0;00m'
>>> codext.decode("\x1b[48;5;130m \x1b[0;00m\x1b[48;5;1m \x1b[0;00m\x1b[48;5;214m \x1b[0;00m\x1b[48;5;11m \x1b[0;00m", "resistors_color")
'1234'
```

-----

### SMS (T9)

This codec implements the SMS encoding, also caled T9, that is the conversion from characters to their corresponding phone keystrokes.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`sms` | text <-> phone keystrokes | `nokia`, `nokia_3310`, `t9` | uses "`-`" as a separator for encoding, "`-`" or "`_`" or whitespace for decoding

```python
>>> codext.encode("this is a test", "sms")
'8-44-444-7777-0-444-7777-0-2-0-8-33-7777-8'
>>> codext.decode("8_44_444_7777_0_444_7777_0_2_0_8_33_7777_8", "nokia")
'this is a test'
>>> codext.decode("8_44_444_7777_0-444-7777_0-2_0_8_33-7777-8", "t9")
'this is a test'
```

-----

### Whitespaces

This simple encoding replaces zeros and ones of the binary version of the input text with spaces and tabs. It is supported either with its original mapping or with the inverted mapping.

!!! warning "Do not confuse"
    
    This should not be confused with the [whitespace esoteric language](https://en.wikipedia.org/wiki/Whitespace_(programming_language)).

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`whitespace` | text <-> whitespaces and tabs | `whitespaces?-inv(erted)?` | The default encoding uses tabs for zeros and spaces for ones
`whitespace_after_before` | text <-> whitespaces[letter]whitespaces | | This codec encodes characters as new characters with whitespaces before and after according to an equation described in the codec name (e.g. "`whitespace+2*after-3*before`")

```python
>>> codext.encode("test", "whitespace")
'\t   \t \t\t\t  \t\t \t \t   \t\t  \t   \t \t\t'
>>> codext.encode("test", "whitespaces")
'\t   \t \t\t\t  \t\t \t \t   \t\t  \t   \t \t\t'
>>> codext.encode("test", "whitespaces-inv")
' \t\t\t \t   \t\t  \t \t \t\t\t  \t\t \t\t\t \t  '
>>> codext.decode(" \t\t\t \t   \t\t  \t \t \t\t\t  \t\t \t\t\t \t  ", "whitespaces_inverted")
'test'
```

```python
>>> codext.encode("test", "whitespace+after-before")
'             m      \n        l               \n   u     \n            m     '
>>> codext.decode("             m      \n        l               \n   u     \n            m     ", "whitespace+after-before")
'test'
```
