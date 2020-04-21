`codext` also defines multiple dummy string manipulation codecs, essentially for use with the CLI tool and for the sake of simplicity.

-----

### Dummy string operations

These "encodings" are simple string transformations, mostly using `str`'s methods.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`capitalize` | text --> capitalized text |  | 
`lowercase` | text --> lowercase text | `lower` | 
`reverse` | text --> reversed text |  | 
`swapcase` | text --> case-swapped text | `swap` | 
`title` | text --> titled text |  | 
`uppercase` | text --> uppercase text | `upper` | 

Of course, these "encodings" have no interest while using them in Python as the `str` methods can be called. It can be useful while using `codext` from the terminal.

Example:

```sh
$ echo -en "test string" | codext reverse | codext upper | codext hex
474E495254532054534554
```
