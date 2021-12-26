# String tranformations

`codext` also defines multiple dummy string manipulation/transformation codecs, essentially for use with the CLI tool and for the sake of simplicity.

-----

### Case-related operations

These transformation functions are simple string transformations, including `str`'s methods.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`camelcase` | text --> camel-case text | `camel` | no decoding
`capitalize` | text <-> capitalized text |  | decoding "uncapitalizes" the text
`lowercase` | text <-> lowercase text | `lower` | decoding is `uppercase`
`pascalcase` | text --> pascal-case text | `pascal` | no decoding
`slugify` | text --> slug | `slug`, `kebab`, `kebabcase` | no decoding
`snakecase` | text --> snake-case text | `snake` | no decoding
`swapcase` | text <-> case-swapped text | `swap` | 
`title` | text <-> titled text |  | decoding "untitles" the text
`uppercase` | text <-> uppercase text | `upper` | decoding is `lowercase`

Of course, these "encodings" have no interest while using them in Python as the `str` methods can be called. It can be useful while using `codext` from the terminal (see [*CLI tool*](cli.html)).

Some simple examples:

```sh
$ echo -en "test string" | codext encode swap-case
TEST STRING

$ echo -en "test string" | codext encode camel_case
testString

$ echo -en "test string" | codext encode kebab_case
test-string
```

-----

### Dummy string operations

These transformation functions are simple string transformations.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`reverse` | text <-> reversed text |  | 
`reverse-words` | text <-> reversed words |  | same as `reverse` but not on the whole text, only on the words (text split by whitespace)

As in the previous section, these "encodings" have no interest while using them in Python but well while using `codext` from the terminal (see [*CLI tool*](cli.html)).

A simple example:

```sh
$ echo -en "test string" | codext encode reverse-words | codext encode reverse
string test
```

Or using encodings chaining:

```sh
$ echo -en "test string" | codext encode reverse-words reverse
string test
```

-----

### Hash functions

These one-way transformation functions rely on the native [`hashlib`](https://docs.python.org/3/library/hashlib.html) library.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`blake2b` | data --> Blake2b(data, length) |  | Python3 only, parametrized ; *length* belongs to [1,64]
`blake2s` | data --> Blake2s(data, length) |  | Python3 only, parametrized ; *length* belongs to [1,32]
`md5` | data --> MD5(data) |  | 
`sha1` | data --> SHA1(data) |  | 
`sha224` | data --> SHA224(data) |  | 
`sha256` | data --> SHA256(data) |  | 
`sha384` | data --> SHA384(data) |  | 
`sha3_224` | data --> SHA3-224(data) |  | Python3 only
`sha3_256` | data --> SHA3-256(data) |  | Python3 only
`sha3_384` | data --> SHA3-384(data) |  | Python3 only
`sha3_512` | data --> SHA3-512(data) |  | Python3 only
`sha512` | data --> SHA512(data) |  | 
`shake_128` | data --> Shake128(data, length) |  | Python3 only, parametrized ; *length* belongs to [1,[
`shake_256` | data --> Shake256(data, length) |  | Python3 only, parametrized ; *length* belongs to [1,[

