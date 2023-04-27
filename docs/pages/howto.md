The purpose of this section is to provide a tutorial for creating new codecs accordingly.

As explained in [this section](./features.html), `codext` provides the possibility to add new codecs in two ways:

1. [`add`](https://github.com/dhondta/python-codext/blob/master/codext/__common__.py#L56): using this function, the *encode* and *decode* functions must be given as arguments.
2. [`add_map`](https://github.com/dhondta/python-codext/blob/master/codext/__common__.py#L160): using this function, an *encoding map* must be given but can be formatted in different ways to handle various use cases.

In both cases, a *pattern* is given in argument and aims to define the set of all strings that aim to select this codec.

!!! important "Codec precedence"
    
    `codext` uses a local registry that is queried first before attempting native `codecs` lookups. This means that a native codec can be overridden with a *pattern* that matches the same strings.

The remainder of this section explains how to successfully create a new codec and/or how to make so that it can be added to the library.

!!! reminder "Contributions welcome !"
    
    Remember that you can always [submit a request for a new codec](https://github.com/dhondta/python-codext/issues/new) or submit your own with a PR for improving `codext` !

-----

### Generic arguments

Whatever solution is chosen, the following arguments shall be considered:

- `ename` (first positional argument): Choose the shortest possible encoding name. If it clashes with another codec, always remember that `codext` resolves codecs in order of registry, that is from the first added. Also, it resolves codecs based on the given pattern. So, a codec with a clashing name could still be selected if the pattern does not match for the codec with the precedence but matches for this codec.
- `pattern` (keyword-argument): If not defined, it defaults to the encoding name. It can be a regular expression ; in this case, it should not be too broad. A codec decode or encode function can be parametrized through the pattern using the **first capture group**. It is important to note that the first capture group is used and not any other. This means that any other group definition shall use the do-not-capture specifier, that is "`(?:...)`".

!!! danger "Too broad pattern"
    
    Let us consider the following ; we add a codec that handles every character in any number of occurrence. It will then capture anything in the given encoding name and will then always resolve to this codec, preventing any other codec added afterwards to resolve.
    
        >>> import codext
        >>> identity = lambda text, errors="strict": (text, len(text))
        >>> codext.add("everything", identity, identity, pattern=r".*")
        >>> codext.encode("test string", "test-encoding-name")  # r".*" matches anything, thus including "test-encoding-name"
        'test string'
        >>> codext.decode("test string", "test-encoding-name")
        'test string'
        >>> codext.encode("test string", "morse")               # "morse" has the precedence on codec "everything" we just added
        '- . ... - / ... - .-. .. -. --.'
        >>> test = lambda text, errors="strict": ("TEST", len(t))
        >>> codext.add("test", test)                            # no pattern given ; should then be matched by encoding name "test"
        >>> codext.encode("test string", "test")                # should give "TEST" if codec "test" was selected
        'test string'                                           # gives the output of codec "test-encoding-name",
                                                                #  which has precedence on "test" and a too broad pattern

-----

### Which `add` function ?

At this point, it is necessary to determine what kind of codec you want. If it is a simple map of characters, you should definitely use [`add_map`](https://github.com/dhondta/python-codext/blob/master/codext/__common__.py#L160). If it is more complex and cannot be handled using [`add_map`](https://github.com/dhondta/python-codext/blob/master/codext/__common__.py#L160)'s options, then you should use [`add`](https://github.com/dhondta/python-codext/blob/master/codext/__common__.py#L56) and define the encode/decode functions yourself.

A few examples:

- `morse` is a simple map that does not handle case ; it then uses [`add_map`](https://github.com/dhondta/python-codext/blob/master/codext/__common__.py#L160) with `ignore_case` set to "`encode`" (not "`both`" for encoding and decoding as it does not matter anyway for decoding)
- `whitespace` has 2 codecs defined ; the simple one is a simple bit encoding map, therefore using [`add_map`](https://github.com/dhondta/python-codext/blob/master/codext/__common__.py#L160) with `intype` set to "`bin`" (for pre-converting characters to bits before applying the encoding map), and the complex one uses [`add`](https://github.com/dhondta/python-codext/blob/master/codext/__common__.py#L56) with its specific endocde/decode functions
- `atbash` defines a dynamic map with a "factory" function, that creates the encoding map according to the parameters supplied in the codec name

So, before going further, determine the following:

- What does the new codec map from and to ? E.g. if binary input and ordinal output, you can use [`add_map`](https://github.com/dhondta/python-codext/blob/master/codext/__common__.py#L160) with `intype="bin"` and `outype="ord"`.
- Is this codec ignoring case ? If so, you can use [`add_map`](https://github.com/dhondta/python-codext/blob/master/codext/__common__.py#L160) and specify which operation(s) should ignore case, e.g. `ignore_case="both"` or `ignore_case="decode"`.
- Should this codec handle no error ? If so, you can use [`add_map`](https://github.com/dhondta/python-codext/blob/master/codext/__common__.py#L160) do not forget to specify `no_error=True`.
- Does the codec yields variable-length encoded tokens ? If so, you can still use [`add_map`](https://github.com/dhondta/python-codext/blob/master/codext/__common__.py#L160) but you should define `sep` (separator) as `codext` will not be able to handle ambiguities.

If you find aspects that are not covered in these questions, you shall use [`add`](https://github.com/dhondta/python-codext/blob/master/codext/__common__.py#L56), then refering to [Case 1](#case-1-generic-encoding-definition). Otherwise, you can use [`add_map`](https://github.com/dhondta/python-codext/blob/master/codext/__common__.py#L160) and refer 
to [Case 2](#case-2-encoding-map).

-----

### Case 1: Generic encoding definition

This uses: [`codext.add`](https://github.com/dhondta/python-codext/blob/master/codext/__common__.py#L56)

The following shall be considered:

- `encode` (keyword-argument ; defaults to `None`): when left `None`, it means that the codec cannot encode.
- `decode` (keyword-argument ; defaults to `None`): when left `None`, it means that the codec cannot decode.

Both functions must take 2 arguments and return 2 values (in order to stick to `codec`'s encode/decode function format):

- Inputs: `text`, `errors="strict"` ; respectively the text to encode/decode and the error handling mode.
- Outputs: encoded text and length of consumed input text.

!!! note "Error handling mode"
    
    - `strict`: this is the default ; it means that any error shall raise an exception.
    - `ignore`: any error is ignored, adding nothing to the output.
    - `replace`: any error yields the given replacement character(s).
    - `leave`: any error yields the erroneous input token in the output.
    
    This last mode is an addition to the native ones. It can be useful for some encodings that must cause no error while encoding and can therefore have their original characters in the output.

Also, while defining the `encode` and/or `decode` functions, `codext.handle_error` can be used as a shortcut to handle the different modes. It returns a wrapped function that takes `token` and `position` as arguments (see [`excess3`](https://github.com/dhondta/python-codext/blob/master/codext/binary/excess3.py) for an example).

```python
>>> help(codext.handle_error)
Help on function handle_error in module codext.__common__:

handle_error(ename, errors, sep='', repl_char='?', repl_minlen=1, decode=False, item='position')
    This shortcut function allows to handle error modes given some tuning parameters.
    
    :param ename:       encoding name
    :param errors:      error handling mode
    :param sep:         token separator
    :param repl_char:   replacement character (for use when errors="replace")
    :param repl_minlen: repeat number for the replacement character
    :param decode:      whether we are encoding or decoding
    :param item:        position item description (for describing the error ; e.g. "group" or "token")

>>> err = codext.handle_error("test", "strict")
>>> help(err)
Help on function _handle_error in module codext.__common__:

_handle_error(token, position)
    This handles an encoding/decoding error according to the selected handling mode.
    
    :param token:    input token to be encoded/decoded
    :param position: token position index

```

-----

### Case 2: Encoding map

This uses: [`codext.add_map`](https://github.com/dhondta/python-codext/blob/master/codext/__common__.py#L160)

The following options shall be considered:

- `encmap` (second positional argument): This defines the encoding map and is the core of the codec ; 4 subcases are handled and explained hereafter.
- `repl_char` (keyword-argument ; default: "`?`"): The replacement character can be tuned, especially if the default one clashes with a character from the encoding.
- `sep` (keyword-argument ; default: ""): The separator between encoded tokens can be useful to tune, especially when the encoded tokens have a variable length.
- `ignore_case` (keyword-argument ; default: `None`): This defines where the case shall be ignored ; it can be one of the followings: "`encode`", "`decode`" or "`both`".
- `no_error` (keyword-argument ; default: `False`): This sets if errors should be handled as normal or if no error should be considered, simply leaving the input token as is in the output.
- `intype` (keyword-argument ; default: `None`): This specifies the type the input text should be converted to before applying the encoding map (pre-conversion before really encoding) ; this can be one of the followings: `str`, `bin` or `ord`.
- `outype` (keyword-argument ; default: `None`): This specifies the type the output text of the encoding map should be converted from (post-conversion after really encoding) ; this can be one of the followings: `str`, `bin` or `ord`.

!!! warning "Input/Output types"
    
    By default, when `intype` is defined, `outype` takes the same value if left `None`. So, if the new encoding uses a pre-conversion to bits (`intype="bin"`) but maps bits to characters (therefore binary conversion to text is not needed), `outype` shall then be explicitely set to "`str`" (or if it maps bits to ordinals, use `outype="ord"`).

`encmap` can be defined as follows:

1. **Simple map**: In this case, the encoding map is a dictionary mapping each input character to an output one (see [`radio`](https://github.com/dhondta/python-codext/blob/master/codext/languages/radio.py) for an example).
2. **List of maps**: In this case, encoding maps are put in a list and referenced by their order number starting from 1, meaning that the `pattern` shall define a capture group with values from 1 to the length of this list (see [`dna`](https://github.com/dhondta/python-codext/blob/master/codext/others/dna.py) for an example).
3. **Parametrized map**: This variant defines a dictionary of regex-selected encoding maps, that is, a dictionary of dictionaries with keys matching the captured groups from codec's pattern.
4. **Map factory function**: This one is implemented by a function that returns the composed encoding map. This function takes a single argument according to the capture group from the `pattern` (see [`affine`](https://github.com/dhondta/python-codext/blob/master/codext/crypto/affine.py) for an example).

!!! note "Mapping one input character to multiple output characters"
    
    In some particular cases (e.g. the `navajo` codec), a single input character can be mapped to multiple output ones. It is possible to define them in a map by simply putting them into a list (e.g. a map with `{'A': ["B", "C", "D"]}`). In this case, while encoding, the output character is randomly chosen (e.g. "`A`" will map to "`D`", another time to "`B`", ...).

-----

### Self-generated tests

In order to facilitate testing, a test suite can be automatically generated from a set of *examples*. This is defined in the `__examples__` dunder inside codec's source file (see [`sms`](https://github.com/dhondta/python-codext/blob/master/codext/stegano/sms.py) for an example). By default, the `add`/`add_map` function will get `__examples__` from the global scope but this behavior can be overridden by specifying the keyword-argument `examples` (e.g. `add(..., examples=__examples1__)` ; see [`ordinal`](https://github.com/dhondta/python-codext/blob/master/codext/common/ordinal.py) for an example).

A set of examples is a dictionary specifying the test cases to be considered. The keys are the descriptions of the test cases and the values can be either dictionaries of input texts and their output encoded texts or lists of input texts. Each key has the format "`operation(encodings)`". Operations can be:

- `enc`: This is for testing the encoding of the nested values (that is, a dictionary of input/outputs).
- `dec`: This is for testing the decoding of the nested values (that is, a dictionary of input/outputs). If this is not specified, the test suite automatically tries to decode from what is defined in `enc`.
- `enc-dec`: This is for testing the encoding AND decoding of the nested values (that is, a list of inputs) ; this one does not enforce what should be the output of the encoding but checks that encoding AND decoding leads to the same input text. This is particularly useful when encoding can yield randomly chosen tokens in the encoded output.

The `encodings` are a `|`-separated list of encoding names, compliant or not with tested codec's pattern. Faulty names can also be tested as of the examples hereafter.

Examples of `__examples__` test suites:

```python
__my_examples__ = {
    'enc(BAD)': None
}
```

!!! note "Observations"
    
    - `__my__examples__` is not the standard dunder, therefore requiring to be specified as the `examples` keyword-argument of `add`/`add_map`.
    - `BAD` is assumed to be a bad encoding name, therefore having a dictionary value of `None`, meaning that the test should raise a `LookupError`.

```python
__examples__ = {
    'enc(codec)': {'string': None}
}
```

!!! note "Observations"
    
    - `__examples__` is the standard dunder, therefore NOT requiring to be specified as the `examples` keyword-argument of `add`/`add_map`.
    - `codec` is assumed to be a valid encoding name, therefore having a dictionary as its value, but in this special case "`string`" is assumed not to be encoded, its corresponding value is then `None`, meaning that the test should raise a `ValueError`.

```python
__examples__ = {
    'enc-dec(codec)': ["test string", "TEST STRING", "@random", "@random{1024}"]
}
```

!!! note "Observations"
    
    - `__examples__` is the standard dunder, thus not specified in `add`/`add_map`.
    - `enc-dec` is used, meaning that a list of inputs is defined.
    - So, whatever its encoded output, the input string shall give the same while applying encoding then decoding.
    - The special values `@random` and `@random{1024}`, meaning that test strings are generated from any possible byte-character with a specified length (512 when not specified, otherwise specified with `{...}`).

```python
__examples__ = {
    'enc(codec)': {"test string": "..."}
}
```

!!! note "Observations"
    
    - `__examples__` is the standard dunder, thus not specified in `add`/`add_map`.
    - `enc` only is used, meaning that a dictionary of inputs/outputs is given and `dec` is automatically handled while requiring the exact encoded text but recovering the exact same input while decoding.

```python
__examples__ = {
    'enc(codec)': {"Test String": "..."},
    'dec(codec)': {"...": "test string"},
}
```

!!! note "Observations"
    
    - `__examples__` is the standard dunder, thus not specified in `add`/`add_map`.
    - `enc` and `dec` are used, meaning that dictionaries of inputs/outputs are given and the input texts are not necessarily the same (i.e. if text case is not handled by the codec).

-----

### Adding a new codec to `codext`

As a checklist when making a codec for addition in `codext`, please follow these steps:

1. Create your codec file (i.e. starting with a copy of an existing similar one)
2. Place it into the right category folder
3. Add it to the list in [`README.md`](https://github.com/dhondta/python-codext/blob/master/README.md#list-of-codecs)
4. Add its documentation in the [right Markdown file](https://github.com/dhondta/python-codext/tree/master/docs/enc)
5. If self-generated tests are not enough, add manual tests in [the related file](https://github.com/dhondta/python-codext/blob/master/tests/test_manual.py)

