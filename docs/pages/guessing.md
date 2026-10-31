For decoding multiple layers of codecs, `codext` features a guess mode relying on an Artificial Intelligence algorithm, the Breadth-First tree Search (BFS). For many cases, the default parameters are sufficient for guess-decoding things. But it may require parameters tuning.

-----

### Parameters

BFS stops when a given condition, in the form of a function applied to the decoded string at the current depth, is met. It returns two results: the decoded string and a tuple with the related encoding names in order of application.

The following parameters are tunable:

- `stop_func`: can be a function or a regular expression to be matched (automatically converted to a function that uses the `re` module) ; by default, checks if all input characters are printable.
- `min_depth`: the minimum depth for the tree search (allows to avoid a bit of overhead while checking the current decoded output at a depth with the stop function when we are sure it should not be the right result) ; by default 0.
- `max_depth`: the maximum depth for the tree search ; by default 5.
- `include`: the [categories](features.md#list-codecs), codecs or encodings to be considered, as a single name, a list of names or a dictionary of lists of names per depth (from 0, -1 meaning any depth) ; by default, `None`, meaning all of them (very slow).
- `exclude`: the [categories](features.md#list-codecs), codecs or encodings not to be considered, in the same formats ; by default, `None`, meaning none of them.
- `found`: a list or tuple of currently found encodings that can be used to save time if the first decoding steps are known ; by default, an empty tuple.

The result is a dictionary of the decoded strings by tuple of encodings, in order of application.

A simple example for a 1-stage base64-encoded string:

```python
>>> codext.guess("VGhpcyBpcyBhIHRlc3Q=")
{('base64',): 'This is a test'}
```

An example of a 2-stages base64- then base62-encoded string:

```python
>>> codext.guess("CJG3Ix8bVcSRMLOqwDUg28aDsT7")
{('chaocipher',): 'NGH3Hb8tYyJWGEEseSOq28aTtS7'}
```

In the second example, we can see that the given encoded string is not decoded as expected. This is the case because the (default) stop condition is too broad and stops if all the characters of the output are printable. If we have a prior knowledge on what we should expect, we can input a simple string or a regex:

!!! note "Default stop function"
    
        :::python
        >>> codext.stopfunc.default.__name__
        '...'
    
    The output depends on whether you have a language detection backend library installed ; see section [*Natural Language Detection*](#natural-language-detection). If no such library is installed, the default function is "`text`".

```python
>>> codext.guess("CJG3Ix8bVcSRMLOqwDUg28aDsT7", "test")
{('base62', 'base64'): 'This is a test'}
```

In this example, the string "*test*" is converted to a function that uses this string as regular expression. Instead of a string, we can also pass a function. For this purpose, standard [stop functions](#available-stop-functions) are predefined. So, we can for instance use `stopfunc.lang_en` to stop when we find something that is English. Note that working this way gives lots of false positives if the text is very short like in the example case. That's why the `include` argument is used to only consider baseX codecs. This is also demonstrated in the next examples.

```python
>>> codext.stopfunc._reload_lang("langdetect")
>>> codext.guess("CJG3Ix8bVcSRMLOqwDUg28aDsT7", codext.stopfunc.lang_en, include="base")
{('base62', 'base64'): 'This is a test'}
```

If we know the first encoding, we can set this in the `found` parameter to save time:

```python
>>> codext.guess("CJG3Ix8bVcSRMLOqwDUg28aDsT7", "test", found=["base62"])
{('base62', 'base64'): 'This is a test'}
```

If we are sure that only `base` (which is a valid [category](features.md#list-codecs)) encodings are used, we can restrict the tree search using the `include` parameter to save time, or even give the encodings to be considered at each depth, while the `exclude` parameter removes some of them:

```python
>>> codext.guess("CJG3Ix8bVcSRMLOqwDUg28aDsT7", "test", include="base")
{('base62', 'base64'): 'This is a test'}
>>> codext.guess("CJG3Ix8bVcSRMLOqwDUg28aDsT7", "test", include={0: ["base62"], 1: ["base64"]})
{('base62', 'base64'): 'This is a test'}
>>> codext.guess("CJG3Ix8bVcSRMLOqwDUg28aDsT7", "test", include="base", exclude="base62")
{}
```

Another example of 2-stages encoded string:

```python
>>> codext.guess("LSAuLi4uIC4uIC4uLiAvIC4uIC4uLiAvIC4tIC8gLSAuIC4uLiAt", "test")
{('base64', 'morse'): 'this is a test'}
>>> codext.guess("LSAuLi4uIC4uIC4uLiAvIC4uIC4uLiAvIC4tIC8gLSAuIC4uLiAt", "test", include=["base", "language"])
{('base64', 'morse'): 'this is a test'}
```

With the [CLI tool](cli.md), these parameters are given with the `-i`/`--include` and `-e`/`--exclude` options, the names being possibly prefixed with a depth (e.g. `codext guess -i 0:base62 1:base64`).

When multiple results are expected, `stop` and `show` arguments can be used respectively to avoid stopping while finding a result and to display the intermediate result.

!!! warning "Computation time"
    
    Note that, in the very last examples, the first call takes much longer than the second one but requires no knowledge about the possible [categories](features.md#list-codecs) of encodings.

-----

### Available Stop Functions

A few stop functions are predefined in the `stopfunc` submodule.

```python
>>> import codext
>>> dir(codext.stopfunc)
['LANG_BACKEND', 'LANG_BACKENDS', ..., '_reload_lang', 'default', 'flag', ..., 'printables', 'regex', 'text']
```

Currently, the following stop functions are provided:

- `flag`:           searches for the pattern "`[Ff][Ll1][Aa4@][Gg9]`" (either UTF-8 or UTF-16)
- `lang_**`:        checks if the given lang is detected (note that it first checks if all characters are text ; see `text` hereafter)
- `printables`:     checks that every output character is in the set of printables
- `regex(pattern)`: takes one argument, the regular expression, for checking a string against the given pattern
- `text`:           checks for printables and an entropy less than 4.6 (empirically determined)

A stop function can be used as the second argument of the `guess` function or as a keyword-argument, as shown in the following examples:

```python
>>> codext.guess("...", codext.stopfunc.text)
[...]
>>> codext.guess("...", [...], stop_func=codext.stopfunc.text)
[...]
```

When a string is given, it is automatically converted to a `regex` stop function.

```python
>>> s = codext.encode("pattern testing", "leetspeak")
>>> s
'p4773rn 73571n9'
>>> stop_func = codext.stopfunc.regex("p[a4@][t7]{2}[e3]rn")
>>> stop_func(s)
True
>>> codext.guess(s, stop_func)
[...]
```

Additionally, a simple stop function is predefined for CTF players, matching various declinations of the word *flag*. Alternatively, a pattern can always be used when flags have a particular format.

```python
>>> codext.stopfunc.flag("test string")
False
>>> codext.stopfunc.flag("test f1@9")
True
>>> codext.stopfunc.regex(r"^CTF\{.*?\}$")("CTF{098f6bcd4621d373cade4e832627b4f6}")
True
```

The particular type of stop function `lang_**` is explained in the [next section](#natural-language-detection).

-----

### Natural Language Detection

As in many cases, we are trying to decode inputs to readable text, it is necessary to narrow the scope while searching for valid decoded outputs. As matching printables and even text (as defined here before as printables with an entropy of less than 4.6) is too broad for many cases, it may be very useful to apply natural language detection. In `codext`, this is done by relying on Natural Language Processing (NLP) backend libraries, loaded only if they were separately installed.

Currently, the following backends are supported, in order of precedence (this order was empirically determined by testing):

- [`langid`](https://github.com/saffsd/langid.py): *Standalone Language Identification (LangID) tool.*
- [`langdetect`](https://github.com/Mimino666/langdetect): *Port of Nakatani Shuyo's language-detection library (version from 03/03/2014) to Python.*
- [`pycld2`](https://github.com/aboSamoor/pycld2): *Python bindings for the Compact Langauge Detect 2 (CLD2).*
- [`cld3`](https://github.com/bsolomon1124/pycld3): *Python bindings to the Compact Language Detector v3 (CLD3).*
- [`textblob`](https://github.com/sloria/TextBlob): *Python (2 and 3) library for processing textual data.*

The way NLP is used is to check that these libraries exist and to take the first one by default. This sets up the `stopfunc.default` for the guess mode. This behavior aims to keep language detection as optional and to avoid multiple specific requirements having the same purpose.

While loaded, the default backend can be switched to another one by using the `_reload_lang` function:
    
```python
>>> codext.stopfunc._reload_lang("pycld2")  # this loads pycld2 and attaches lang_** functions to the stopfunc submodule
>>> codext.stopfunc._reload_lang()          # this unloads any loaded backend
```

Each time a backend is loaded, it gets `lang_**` stop functions attached to the `stopfunc` submodule for each supported language.

-----

### Ranking Heuristic

At each step of the search, the candidate encodings are decoded and ranked with a score, the best ones being tried first. The score combines characteristics of the input compared to those expected by each codec (length of its charset, padding, rate of printable characters, expansion factor and entropy) and a characteristic of the decoded output: how much it looks like a text.

This "textness" depends on the script of the letters. For Latin letters, it is mainly given by the rate of common bigrams among the pairs of successive letters (around 70% for English texts, against around 15% for random letters ; most of these bigrams are also common in other Latin-script languages such as French, German, Spanish or Italian), weighted by the rates of printable characters and of letters and spaces, and by the number of distinct letters. For other scripts (e.g. Cyrillic, Greek, Arabic or CJK), it only relies on language-independent features: the rate of letters of the dominant script, the rate of letters, spaces and punctuation, and the length of the words (for the scripts that separate words with spaces). As these features cannot distinguish a text from a substitution of its characters, the outputs of such codecs are only rated from Latin letters. A bonus is given when the output looks like a text (textness above 0.5) and more than the input, which favours the right decoding over transformations that never fail (e.g. keyboard shifts) without favouring wrong decodings in a chain of encodings. Codecs that only substitute characters (e.g. `rot`, `xor`, `kbshift`) also get a penalty when their output looks less like a text than their input.

!!! warning "Work in progress"
    
    This part shall still be improved with better features and/or using machine learning. In particular, the default stop function (`text`) accepts any printable output with a low entropy, hence possibly an intermediate result of a chain of encodings.

