Basically, the `codecs` library provides a series of functions from the built-in `_codecs` library which maintains a registry of search functions (a simple list) that maps ancodings to the right de/encode functions by returning a `CodecInfo` object once first matched.

`codext` hooks `codecs`'s functions to insert its own proxy registry between the function calls and the native registry so that new encodings can be added or replace existing ones while using `code[cs|xt].open`. Indeed, as the proxy registry is called first, the first possible match occurs in a custom codec, while if not existing, the native registry is used.

!!! note "The `open` built-in function"
    
    Two behaviors are to be considered when using `codext`:
    
    1. Encodings added from `codext` are only added to the proxy codecs registry of `codext` and are NOT available using `open(...)` (but well using `code[cs|xt].open(...)`.
    2. Encodings added from `codecs` are added to the proxy registry AND ALSO to the native registry and are therefore available using `open(...)`.
    
    This difference allows to keep encodings added from `codext` removable while these added from `codecs` are not. This is the consequence from the fact that there is no unregister function in the native `_codecs` library.

!!! warning "Lossy conversion"
    
    Some encodings are lossy, meaning that it is not always possible to decode back to the exact start string. This should be considered especially when chaining codecs.

-----

### Add a custom encoding

New codecs can be added easily using the new function `add`.

```python
>>> import codext
>>> help(codext.add)
Help on function add in module codext.__common__:

add(ename, encode=None, decode=None, pattern=None, text=True, add_to_codecs=False)
    This adds a new codec to the codecs module setting its encode and/or decode
     functions, eventually dynamically naming the encoding with a pattern and
     with file handling (if text is True).
    
    :param ename:           encoding name
    :param encode:          encoding function or None
    :param decode:          decoding function or None
    :param pattern:         pattern for dynamically naming the encoding
    :param text:            specify whether the codec is a text encoding
    :param add_to_codecs:   also add the search function to the native registry
                            NB: this will make the codec available in the
                                 built-in open(...) but will make it impossible
                                 to remove the codec later

```

Here is a simple example of how to add a basic codec:

```python
import codext

def mycodec_encode(text, errors="strict"):
    # do some encoding stuff
    return encoded, len(text)

def mycodec_decode(text, errors="strict"):
    # do some decoding stuff
    return decoded, len(text)

codext.add("mycodec", mycodec_encode, mycodec_decode)
```

In this first example, we can see that:

- The `decode`/`encode` functions have a signature holding a keyword-argument "`errors`" for error handling. This comes from the syntax for making a codec for the `codecs` native library. This argument can have multiple values, namely "`strict`" for raising an exception when an de/encoding error occurs, while "`replace`" allows to replace the character at the position of the error with a generic character and also "`ignore`" that simply ignores the error and continues without adding anything to the resulting string.
- These functions always return a pair with the resulting string and the length of consumed input text.

Another example for a more complex and dynamic codec:

```python
import codext

def mydyncodec_encode(i):
    def encode(text, error="strict"):
        # do somthing depending on i
        return result, len(text)
    return encode

codext.add("mydyncodec", mydyncodec_encode, pattern=r"mydyn-(\d+)$")
```

In this second example, we can see that:

- Only the encoding function is defined.
- A pattern is defined to match the prefix "`mydyn-`" and then an integer which is captured and used with `mydyncodec_encode(i)`.

!!! warning "Pattern capture group"
    
    A capture group means that the parameter will be used with a dynamic (decorated) encoding function. In order to avoid this, i.e. for matching multiple names leading to the same encoding while calling a static encoding function, we can simply define a non-capturing group, e.g. "`(?:my|special_)codec`".

-----

### Add a custom map encoding

New codecs using encoding maps can be added easily using the new function `add_map`.

```python
>>> import codext
>>> help(codext.add)
Help on function add_map in module codext.__common__:

add_map(ename, encmap, repl_char='?', sep='', ignore_case=None, no_error=False, intype=None, outype=None, **kwargs)
    This adds a new mapping codec (that is, declarable with a simple character mapping dictionary) to the codecs module
     dynamically setting its encode and/or decode functions, eventually dynamically naming the encoding with a pattern
     and with file handling (if text is True).
    
    :param ename:         encoding name
    :param encmap:        characters encoding map ; can be a dictionary of encoding maps (for use with the first capture
                           group of the regex pattern) or a function building the encoding map
    :param repl_char:     replacement char (used when errors handling is set to "replace")
    :param sep:           string of possible character separators (hence, only single-char separators are considered) ;
                           - while encoding, the first separator is used
                           - while decoding, separators can be mixed in the input text
    :param ignore_case:   ignore text case while encoding and/or decoding
    :param no_error:      this encoding triggers no error (hence, always in "leave" errors handling)
    :param intype:        specify the input type for pre-transforming the input text
    :param outype:        specify the output type for post-transforming the output text
    :param pattern:       pattern for dynamically naming the encoding
    :param text:          specify whether the codec is a text encoding
    :param add_to_codecs: also add the search function to the native registry
                           NB: this will make the codec available in the built-in open(...) but will make it impossible
                                to remove the codec later

```

This relies on the [`add`](#add-a-custom-encoding) function and simplifies creating new encodings when they can be described as a mapping dictionary.

Here is a simple example of how to add a map codec:

```python
import codext

ENCMAP = {'a': "A", 'b': "B", 'c': "C"}

codext.add_map("mycodec", ENCMAP)
```

In this first example, we can see that:

- The `decode`/`encode` functions do not have to be declared anymore.
- `ENCMAP` is the mapping between characters, it is also used to compute the decoding function.

Another example for a more complex and dynamic codec:

```python
import codext

ENCMAP = [
    {'00': "A", '01': "B", '10': "C", '11': "D"},
    {'00': "D", '01': "C", '10': "B", '11': "A"},
]

codext.add("mydyncodec", ENCMAP, "#", ignore_case=True, intype="bin", pattern=r"mydyn-(\d+)$")
```

In this second example, we can see that:

- `ENCMAP` is now a list of mappings. The capture group in the pattern is used to select the right encoding map. Consequently, using encoding "`mydyn-8`" will fail with a `LookupError` as the only possibility are "`mydyn-1`" and "`mydyn-2`". Note that the index begins at 1 in the encoding name.
- Instead of using the default character "`?`" for replacements, we use "`#`".
- The case is ignored ; decoding either "`abcd`" or "`ABCD`" will succeed.
- The binary mode is enabled, meaning that the input text is converted to a binary string for encoding, while it is converted from binary to text when decoding.

!!! warning "Input/Output types"
    
    By default, when `intype` is defined, `outype` takes the same value. So, if the new encoding uses a pre-conversion to bits (`intype="bin"`) but maps bits to characters (therefore binary conversion to text is not needed), `outype` shall then be set to "`str`" (or if it maps bits to ordinals, use `outype="ord"`).

-----

### Add a macro

**Macros** are chains of encodings. It is possible to define own macros with this feature. It works by giving the precedence to user's macros saved in `~/.codext-macros.json` then using embedded macros from the `codext` package.

Here is an example of adding a macro (and verifying it was indeed added):

```python
>>> codext.list_macros()
['example-macro']
>>> codext.add_macro("test-macro", "gzip", "base64")
>>> codext.list_macros()
['example-macro', 'test-macro']
```

!!! note "Removing a macro"
    
    As macros are resolved like codecs (with the precedence for codecs), they can be removed the same way as a codec.
    
        :::python
        >>> codext.remove("test-macro")
    
    If this is a built-in macro, it will removed from the runtime list within the `codext` package. Next time this will be loaded, it will reset the builtin list of macros. Otherwise, if this is a custom macro, it will removed from the list of custom macros AND removed from `~/.codext-macros.json`.

-----

### List codecs

Codecs can be listed with the `list` function, either the whole codecs or only some categories.

```python
>>> codext.list()
['affine', 'ascii', 'ascii85', 'atbash', 'bacon', ..., 'base36', 'base58', 'base62', 'base64', 'base64_codec', ..., 'baudot-tape', 'bcd', 'bcd-extended0', 'bcd-extended1', 'big5', 'big5hkscs', 'braille', 'bz2_codec', 'capitalize', 'cp037', ...]
```

!!! note "Codecs categories"
    
    - `native`: the built-in codecs from the original `codecs` package
    - `non-native`: this special category regroups all the categories mentioned hereafter
    - `base`: baseX codecs (e.g. `base`, `base100`)
    - `binary`: codecs working on strings but applying their algorithms on their binary forms (e.g. `baudot`, `manchester`)
    - `common`: common codecs not included in the native ones or simly added for the purpose of standardization (e.g. `octal`, `ordinal`)
    - `crypto`: codecs related to cryptography algorithms (e.g. `barbie`, `rot`, `xor`)
    - `language`: language-related codecs (e.g. `morse`, `navajo`)
    - `other`: uncategorized codecs (e.g. `letters`, `url`)
    - `stegano`: steganography-related codecs (e.g. `sms`, `resistor`)
    
    Except the `native` and `non-native` categories, the other ones are simply the name of the subdirectories (with "`s`" right-stripped) of the `codext` package.

```python
>>> codext.list("binary")
['baudot', 'baudot-spaced', 'baudot-tape', 'bcd', 'bcd-extended0', 'bcd-extended1', 'excess3', 'gray', 'manchester', 'manchester-inverted']
>>> codext.list("language")
['braille', 'leet', 'morse', 'navajo', 'radio', 'southpark', 'southpark-icase', 'tom-tom']
>>> codext.list("native")
['ascii', 'base64_codec', 'big5', 'big5hkscs', 'bz2_codec', 'cp037', 'cp273', 'cp424', 'cp437', 'cp500', 'cp775', 'cp850', 'cp852', 'cp855', 'cp857', 'cp858', 'cp860', 'cp861', 'cp862', 'cp863', ...]
```

!!! warning "Codecs listed, not encodings"
    
    Beware that this function only lists the codecs, not the encodings. This means that, for instance, it only lists `base` (codecs' name) instead of `base17`, `base61`, `base97`, ... (the valid encoding names related to the `base` codec).

-----

### Search for encodings

Natively, `codecs` provides a `lookup` function that allows to get the `CodecInfo` object for the desired encoding. This performs a lookup in the registry based on an exact match. Sometimes, it can be useful to search for available encodings based on a regular expression. Therefore, a `search` function is added by `codext` to allow to get a list of encoding names matching the input regex.

```python
>>> codext.search("baudot")
['baudot', 'baudot_spaced', 'baudot_tape']
>>> codext.search("al")
['capitalize', 'octal', 'octal_spaced', 'ordinal', 'ordinal_spaced', 'radio']
>>> codext.search("white")
['whitespace', 'whitespace_after_before']
```

Also, `codext` provides an `examples` function to get some examples of valid encoding names. This is especially useful when it concerns dynamicly named encodings (e.g. `rot`, `shift` or `dna`).

```python
>>> codext.examples("rot")
['rot-14', 'rot-24', 'rot-7', 'rot18', 'rot3', 'rot4', 'rot6', 'rot_1', 'rot_12', 'rot_2']
>>> codext.examples("dna")
['dna-1', 'dna-2', 'dna-5', 'dna1', 'dna4', 'dna5', 'dna6', 'dna8', 'dna_3', 'dna_5']
>>> codext.examples("barbie", 5)
['barbie-1', 'barbie1', 'barbie4', 'barbie_2', 'barbie_4']
```

-----

### Remove a custom encoding or macro

New codecs can be removed easily using the new function `remove`, which will only remove every codec matching the given encoding name in the proxy codecs registry and NOT in the native one.

```python
>>> codext.encode("test", "bin")
'01110100011001010111001101110100'
>>> codext.remove("bin")
>>> codext.encode("test", "bin")

Traceback (most recent call last):
  [...]
LookupError: unknown encoding: bin
```

Trying to remove a codec that is in the native registry won't raise a `LookupError`.

```python
>>> codext.remove("utf-8")
>>> codext.encode("test", "utf-8")
b'test'
```

Removing a macro works exactly the same way as for a codec.

```python
>>> codext.remove("test-macro")
```

-----

### Remove or restore `codext` encodings and macros

It can be useful while playing with encodings and/or macros e.g. from Idle to be able to remove or restore `codext`'s encodings and macros. This can be achieved using respectively the new `clear` and `reset` functions.

```python
>>> codext.clear()
>>> codext.encode("test", "bin")

Traceback (most recent call last):
  [...]
LookupError: unknown encoding: bin
```

```python
>>> codext.reset()
>>> codext.encode("test", "bin")
'01110100011001010111001101110100'
```

-----

### Multi-rounds encoding

It is possible to use multiple times the same encoding through the following convention: `encoding[X]`

A simple example for a 1-round and a 2-rounds morse-encoded string:

```python
>>> codext.encode("This is a test", "morse")
'- .... .. ... / .. ... / .- / - . ... -'
>>> codext.encode("This is a test", "morse[2]")
'-....- / .-.-.- .-.-.- .-.-.- .-.-.- / .-.-.- .-.-.- / .-.-.- .-.-.- .-.-.- / -..-. / .-.-.- .-.-.- / .-.-.- .-.-.- .-.-.- / -..-. / .-.-.- -....- / -..-. / -....- / .-.-.- / .-.-.- .-.-.- .-.-.- / -....-'
```

Another example using 5-rounds base58:

```python
>>> codext.encode("Sup3rS3cr3t", "base58[5]")
'3YrjaeeJE1qfUVkpUbMymEMLJenvRrtcZ4vaDQ3httdiqWV8wGYFpqw'
```

-----

### Hooked `codecs` functions

In order to select the right de/encoding function and avoid any conflict, the native `codecs` library registers search functions (using the `register(search_function)` function), called in order of registration while searching for a codec.

While being imported, `codext` hooks the following base functions of `codecs` dealing with the codecs registry: `encode`, `decode`, `lookup` and `register`. This way, `codext` holds a private registry that is called before reaching out to the native one, causing the codecs defined in `codext` to override native codecs with a matching registry search function.

