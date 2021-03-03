`codext` has a Command-Line Interface tool.

-----

### Using Codext from the terminal

The help message describes everything to know:

```sh
usage: codext [-h] [-i INFILE] [-o OUTFILE] [-s] {encode,decode,guess,search} ...

Codecs Extension (CodExt) 1.8.1

Author   : Alexandre D'Hondt (alexandre.dhondt@gmail.com)
Copyright: © 2019-2021 A. D'Hondt
License  : GPLv3 (https://www.gnu.org/licenses/gpl-3.0.fr.html)
Source   : https://github.com/dhondta/python-codext

This tool allows to encode/decode input strings/files with an extended set of codecs.

positional arguments:
  {encode,decode,guess,search}
                        command to be executed
    encode              encode input using the specified codecs
    decode              decode input using the specified codecs
    guess               try guessing the decoding codecs
    search              search for codecs

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE, --input-file INFILE
                        input file (if none, take stdin as input)
  -o OUTFILE, --output-file OUTFILE
                        output file (if none, display result to stdout)
  -s, --strip-newlines  strip newlines from input

usage examples:
- codext search bitcoin
- codext decode base32 -i file.b32
- codext encode morse < to_be_encoded.txt
- echo "test" | codext encode base100
- echo -en "test" | codext encode braille -o test.braille
- codext encode base64 < to_be_encoded.txt > text.b64
- echo -en "test" | codext encode base64 | codext encode base32
- echo -en "mrdvm6teie6t2cq=" | codext encode upper | codext decode base32 | codext decode base64
- echo -en "test" | codext encode upper reverse base32 | codext decode base32 reverse lower
- echo -en "test" | codext encode upper reverse base32 base64 morse
- echo -en "test" | codext encode base64 gzip | codext guess
- echo -en "test" | codext encode base64 gzip | codext guess gzip -c base
```

!!! note "Input/output"
    
    STDIN can be used as shown in an example from the help message, like when using the common Linux tool `base64`.
    
    Unless an output file is specified, the result is displayed in STDOUT.

!!! note "Encodings chaining"
    
    Encodings can be chained as shown in the last examples of the help message. This can be practical for quickly manipulating data.

