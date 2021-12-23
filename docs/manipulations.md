# String manipulations

`codext` also defines multiple dummy string manipulation codecs, essentially for use with the CLI tool and for the sake of simplicity.

-----

### Case-related operations

These "encodings" are simple string transformations, including `str`'s methods.

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

These "encodings" are also simple string transformations.

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
