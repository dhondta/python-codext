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
`screamingsnakecase` | text --> screaming-snake-case text | `screaming-snake`, `screaming_snake_case` | no decoding
`slugify` | text --> slug | `slug`, `kebab`, `kebabcase` | no decoding
`snakecase` | text --> snake-case text | `snake` | no decoding
`swapcase` | text <-> case-swapped text | `swap`, `invert`, `invertcase` | 
`title` | text <-> titled text |  | decoding "untitles" the text
`uppercase` | text <-> uppercase text | `upper` | decoding is `lowercase`

Of course, these transformations have no interest while using them in Python as the `str` methods can be called. It can be useful while using `codext` from the terminal (see [*CLI tool*](cli.html)).

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
`replace` | text <-> text with multi-chars replaced |  | parametrized with a _string_ and its _replacement_
`reverse` | text <-> reversed text |  | 
`reverse-words` | text <-> reversed words |  | same as `reverse` but not on the whole text, only on the words (text split by whitespace)
`strip-spaces` | text <-> all whitespaces stripped |  | 
`substitute` | text <-> text with token substituted |  | 
`tokenize` | text <-> text split in tokens of length N |  | parametrized with _N_

As in the previous section, these transformations have no interest while using them in Python but well while using `codext` from the terminal (see [*CLI tool*](cli.html)).

A simple example:

```sh
$ echo -en "test string" | codext encode reverse-words | codext encode reverse replace-\ _
string_test
```

Another example:

```sh
$ echo -en "3132333435" | codext encode tokenize-2
31 32 33 34 35
```

Or using encodings chaining:

```sh
$ echo -en "test string" | codext encode reverse-words reverse substitute-string/phrase
phrase test
```

