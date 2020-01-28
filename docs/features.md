Basically, the `codecs` library, relying on the built-in `_codecs` library, maintains a registry of search functions that maps an input `encoding` variable to the right de/encode function. `codext` hooks the native `codecs` to insert its own registry between the function calls and the native one.

!!! note "`codecs` import and the `open` built-in function"
    
    When `codext` is imported, the new encodings are added to its registry but also to the native one. Moreover, hooked functions are bound to the `codext` module but also overwrites the original ones in `codecs`. Consequently:
    
    1. Once `codext` has been imported, `codecs` can be imported elsewhere in the program and will have the `add` and hooked functions attached, with the new encodings available.
    2. While `codecs.open` will handle the new encodings according to `codext`'s registry first, the native `open` function will rely on the native registry only and therefore handle the encoding search functions of `codext` _after_ these of the native registry has it will rely on non-hooked functions.

-----

## Add a custom encoding

New codecs can be added easily using the new function `add`.

```python
>>> import codext
>>> help(codext.add)
Help on function add in module codext.__common__:

add(ename, encode=None, decode=None, pattern=None, text=True)
    This adds a new codec to the codecs module setting its encode and/or decode
     functions, eventually dynamically naming the encoding with a pattern and
     with file handling (if text is True).
    
    :param ename:   encoding name
    :param encode:  encoding function or None
    :param decode:  decoding function or None
    :param pattern: pattern for dynamically naming the encoding
    :param text:    specify whether the codec is a text encoding

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

## Hooked `codecs` functions

In order to select the right de/encoding function and avoid any conflict, the native `codecs` library registers search functions (using the `register(search_function)` function), called in order of registration while searching for a codec.

While being imported, `codext` hooks the following base functions of `codecs` dealing with the codecs registry: `encode`, `decode`, `lookup` and `register`. This way, `codext` holds a private registry that is called before reaching out to the native one, causing the codecs defined in `codext` to override native codecs with a matching registry search function.
