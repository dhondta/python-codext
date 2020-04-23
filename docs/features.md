Basically, the `codecs` library provides a series of functions from the built-in `_codecs` library which maintains a registry of search functions (a simple list) that maps ancodings to the right de/encode functions by returning a `CodecInfo` object once first matched.

`codext` hooks `codecs`'s functions to insert its own proxy registry between the function calls and the native registry so that new encodings can be added or replace existing ones while using `code[cs|xt].open`. Indeed, as the proxy registry is called first, the first possible match occurs in a custom codec, while if not existing, the native registry is used.

!!! note "The `open` built-in function"
    
    Two behaviors are to be considered when using `codext`:
    
    1. Encodings added from `codext` are only added to the proxy codecs registry of `codext` and are NOT available using `open(...)` (but well using `code[cs|xt].open(...)`.
    2. Encodings added from `codecs` are added to the proxy registry AND ALSO to the native registry and are therefore available using `open(...)`.
    
    This difference allows to keep encodings added from `codext` removable while these added from `codecs` are not. This is the consequence from the fact that there is no unregister function in the native `_codecs` library.

-----

## Add a custom encoding

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
- The `text=True` keyword-argument could have been used to only support text de/encoding and not file handling.

!!! warning "Pattern capture group"
    
    A capture group means that the parameter will be used with a dynamic (decorated) encoding function. In order to avoid this, i.e. for matching multiple names leading to the same encoding while calling a static encoding function, we can simply define a non-capturing group, e.g. "`(?:my|special_)codec`".

-----

## Add a custom map encoding

New codecs using encoding maps can be added easily using the new function `add_map`.

```python
>>> import codext
>>> help(codext.add)
Help on function add_map in module codext.__common__:

add_map(ename, encmap, repl_char='?', sep='', ignore_case=False, no_error=False, binary=False, **kwargs)
    This adds a new mapping codec (that is, declarable with a simple character mapping dictionary) to the codecs module
     dynamically setting its encode and/or decode functions, eventually dynamically naming the encoding with a pattern
     and with file handling (if text is True).
    
    :param ename:         encoding name
    :param encmap:        characters encoding map ; can be a dictionary of encoding maps (for use with the first capture
                           group of the regex pattern)
    :param repl_char:     replacement char (used when errors handling is set to "replace")
    :param sep:           string of possible character separators (hence, only single-char separators are considered) ;
                           - while encoding, the first separator is used
                           - while decoding, separators can be mixed in the input text
    :param ignore_case:   ignore text case
    :param no_error:      this encoding triggers no error (hence, always in "leave" errors handling)
    :param binary:        encoding applies to the binary string of the input text
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

codext.add("mydyncodec", ENCMAP, "#", ignore_case=True, binary=True, pattern=r"mydyn-(\d+)$")
```

In this second example, we can see that:

- `ENCMAP` is now a list of mappings. The capture group in the pattern is used to select the right encoding map. Consequently, using encoding "`mydyn-8`" will fail with a `LookupError` as the only possibility are "`mydyn-1`" and "`mydyn-2`". Note that the index begins at 1 in the encoding name.
- Instead of using the default character "`?`" for replacements, we use "`#`".
- The case is ignored ; decoding either "`abcd`" or "`ABCD`" will succeed.
- The binary mode is enabled, meaning that the input text is converted to a binary string for encoding, while it is converted from binary to text when decoding.

-----

## Remove a custom encoding

New codecs can be removed easily using the new function `remove`, which will only remove every codec matching the given encoding name in the proxy codecs registry and NOT in the native one.

```python
>>> codext.encode("test", "bin")
'01110100011001010111001101110100'
>>> codext.remove("bin")
>>> codext.encode("test", "bin")

Traceback (most recent call last):
  File "<pyshell#39>", line 1, in <module>
    codext.encode("test", "bin")
  File "codext/__common__.py", line 245, in __encode
    return __lookup(encoding).encode(obj, errors)[0]
  File "codext/__common__.py", line 259, in __lookup
    codecs.lookup = __lookup
LookupError: unknown encoding: bin
```

While trying to remove a codec that is in the native registry won't raise a `LookupError`.

```python
>>> codext.remove("utf-8")
>>> codext.encode("test", "utf-8")
b'test'
```

-----

## Remove or restore `codext` encodings

It can be useful while playing with encodings e.g. from Idle to be able to remove or restore `codext`'s encodings. This can be achieved using respectively the new `clear` and `reset` functions.

```python
>>> codext.clear()
>>> codext.encode("test", "bin")
Traceback (most recent call last):
  File "<pyshell#4>", line 1, in <module>
    codext.encode("test", "bin")
  File "/mnt/data/Projects/maint/python-codext/codext/__common__.py", line 245, in __encode
    return __lookup(encoding).encode(obj, errors)[0]
  File "/mnt/data/Projects/maint/python-codext/codext/__common__.py", line 258, in __lookup
    return orig_lookup(encoding)
LookupError: unknown encoding: bin
```

```python
>>> codext.reset()
>>> codext.encode("test", "bin")
'01110100011001010111001101110100'
```

-----

## Hooked `codecs` functions

In order to select the right de/encoding function and avoid any conflict, the native `codecs` library registers search functions (using the `register(search_function)` function), called in order of registration while searching for a codec.

While being imported, `codext` hooks the following base functions of `codecs` dealing with the codecs registry: `encode`, `decode`, `lookup` and `register`. This way, `codext` holds a private registry that is called before reaching out to the native one, causing the codecs defined in `codext` to override native codecs with a matching registry search function.
