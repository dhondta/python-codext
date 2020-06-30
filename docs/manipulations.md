`codext` also defines multiple dummy string manipulation codecs, essentially for use with the CLI tool and for the sake of simplicity.

-----

### Dummy string operations

These "encodings" are simple string transformations, mostly using `str`'s methods.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`capitalize` | text <-> capitalized text |  | decoding "uncapitalizes" the text
`lowercase` | text <-> lowercase text | `lower` | decoding is `uppercase`
`reverse` | text <-> reversed text |  | 
`reverse-words` | text <-> reversed words |  | same as `reverse` but not on the whole text, only on the words (text split by whitespace)
`swapcase` | text <-> case-swapped text | `swap` | 
`title` | text <-> titled text |  | decoding "untitles" the text
`uppercase` | text <-> uppercase text | `upper` | decoding is `lowercase`

Of course, these "encodings" have no interest while using them in Python as the `str` methods can be called. It can be useful while using `codext` from the terminal (see [*CLI tool*](cli.md)).

A simple example:

```sh
$ echo -en "test string" | codext reverse | codext upper | codext hex
474E495254532054534554
```

Or using encodings chaining:

```sh
$ echo -en "test string" | codext reverse upper hex
474E495254532054534554
```
