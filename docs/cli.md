`codext` has a Command-Line Interface tool.

-----

### Using Codext from the terminal

The help message describes everything to know:

```sh
$ codext --help
usage: codext [-h] [-d] [-e {ignore,leave,replace,strict}] [-i INFILE]
              [-o OUTFILE] [-s]
              encoding [encoding ...]

Codecs Extension (CodExt) 1.4.0

Author   : Alexandre D'Hondt (alexandre.dhondt@gmail.com)
Copyright: © 2019-2020 A. D'Hondt
License  : AGPLv3 (http://www.gnu.org/licenses/agpl.html)
Source   : https://github.com/dhondta/python-codext

This tool allows to encode/decode input strings/files with an extended set of codecs.

positional arguments:
  encoding              list of encodings to apply

optional arguments:
  -h, --help            show this help message and exit
  -d, --decode          set decode mode
  -e {ignore,leave,replace,strict}, --errors {ignore,leave,replace,strict}
                        error handling
  -i INFILE, --input-file INFILE
                        input file (if none, take stdin as input)
  -o OUTFILE, --output-file OUTFILE
                        output file (if none, display result to stdout)
  -s, --strip-newlines  strip newlines from input

usage examples:
- codext -d base32 -i file.b32
- codext morse < to_be_encoded.txt
- echo "test" | codext base100
- echo -en "test" | codext braille -o test.braille
- codext base64 < to_be_encoded.txt > text.b64
- echo -en "test" | codext base64 | codext base32
- echo -en "mrdvm6teie6t2cq=" | codext upper | codext -d base32 | codext -d base64
- echo -en "test" | codext upper reverse base32 base64 morse
```

!!! note "Input/output"
    
    STDIN can be used as shown in an example from the help message, like when using the common Linux tool `base64`.
    
    Unless an output file is specified, the result is displayed in STDOUT.

!!! note "Encodings chaining"
    
    Encodings can be chained as shown in the last examples of the help message. This can be practical for quickly manipulating data.
