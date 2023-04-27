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

### Execution examples

**Scenario 1**: 2-stages encoded flag

Creating the payload:

```session
$ echo "A somewhat weird F1@9 !" | codext encode rotate-3 base58
pwTDSWRUbXTuMQs5EDgKpjgW8MiJVw1
```

From this point, the only thing we know is that we are searching for "*flag*" (with eventually other characters, i.e. leetspeak).

```session
$ echo "A somewhat weird F1@9 !" | codext encode rotate-3 base58 | codext guess -f flag
Codecs: base58, rotate-3
A somewhat weird F1@9 !
```

Executing the previous command will take a few tens of seconds. With few stages to be guessed, using the scoring heuristic can be far quicker to get to the right output. The following takes less than a second.

```session
$ echo "A somewhat weird F1@9 !" | codext encode rotate-3 base58 | codext guess -f flag --heuristic
Codecs: base58, rotate-3
A somewhat weird F1@9 !
```

**Scenario 2**: Multi-stage-encoded flag

Creating the payload:

```session
$ echo "A somewhat weird F1@9 !" | codext encode barbie-1 base32 morse
.... -.-- --.- --. -- ....- - -.- -- . ..... -..- --. ..--- .-.. .. . .- ..... .-- -.-. ..... -.. --- -. --.- --.- . --. -- .-. --... ..-. ..- --.- -.-. -- -...- -...- -...-
```

When looking at the string, it is easy to figure out it is morse. The problem, at this point, is that this codec is case-insensitive and always returns lowercase characters, as shown hereafter.

```session
$ echo "A somewhat weird F1@9 !" | codext encode barbie-1 base32 morse | codext decode morse
hyqgm4tkme5xg2liea5wc5donqqegmr7fuqcm===
```

In order to get it guessed as Base32, it is necessary to put it back to uppercase (in other words, decode from lowercase).

```session
$ echo "A somewhat weird F1@9 !" | codext encode barbie-1 base32 morse | codext decode morse lowercase
HYQGM4TKME5XG2LIEA5WC5DONQQEGMR7FUQCM===
```

Now that we know we are searching for something with "*flag*" (with eventually other characters), we can use the predefined "`flag`" stop function.

```session
$ echo "A somewhat weird F1@9 !" | codext encode barbie-1 base32 morse | codext decode morse lowercase | codext guess -f flag
Codecs: base32, barbie
A somewhat weird F1@9 !
```

**Scenario 3**: Base-encoded rotated shifted secret (English) message

Creating the payload:

```session
$ echo "My super secret string" | codext encode shift-1 rotate-2 base58 base64
NDNxaFdieXh0Z29XOVZpWWpjRGNpRWgyZE44Z2FNU0g=
```

First, we shall simplify as much as possible ; we can easily guess that Base64 was used as the first encoding scheme:

```session
$ echo "aDRuUnFGaWZTblJqRmZReFJIdVZweGp4cFA4Y0NS" | codext rank
[+] 1.00002: base62
[+] 0.99401: base64
[+] 0.70806: rotate-1
[+] 0.70806: rotate-2
[+] 0.70806: rotate-3
[+] 0.70806: rotate-4
[+] 0.70806: rotate-5
[+] 0.70806: rotate-6
[+] 0.70806: rotate-7
[+] 0.70806: rotate-left-1

$ echo "aDRuUnFGaWZTblJqRmZReFJIdVZweGp4cFA4Y0NS" | codext decode base62
%¤q ´!.[æ&[fÿhbð^

$ echo "aDRuUnFGaWZTblJqRmZReFJIdVZweGp4cFA4Y0NS" | codext decode base64
h4nRqFifSnRjFfQxRHuVpxjxpP8cCR
```

Afterwards, we can still try to simplify ;

```session
$ echo "aDRuUnFGaWZTblJqRmZReFJIdVZweGp4cFA4Y0NS" | codext decode base64 | codext rank
[+] 1.00185: base58
[+] 0.99091: base62
[+] 0.67001: rotate-1
[+] 0.67001: rotate-2
[+] 0.67001: rotate-3
[+] 0.67001: rotate-4
[+] 0.67001: rotate-5
[+] 0.67001: rotate-6
[+] 0.67001: rotate-7
[+] 0.67001: rotate-left-1
```

From here, let us assume that `base58` is effectively the right second-stage encoding. Guessing the two remaining encodings with no more information will now take a few seconds. As multiple outputs can be recognized as normal text, we will use the "`-s`" option not to stop on the first output successfully decoded as text. Moreover, if we have the intuition that the output shall be English text, we can use a more refined stop function like "`lang_en`" with the "`-f`" option.

```session
$ echo "aDRuUnFGaWZTblJqRmZReFJIdVZweGp4cFA4Y0NS" | codext decode base64 | codext decode base58 | codext guess -s -f lang_en
[...]
[+] rotate-2, rot-1: My!super!secret!string
[+] rotate-2, rot-23: Qc!wytiv!wigvix!wxvmrk
[+] rotate-2, shift-1: My super secret string
[+] rotate-2, shift-20: :f\r`b]R_\r`RP_Ra\r`a_V[T
[...]
[+] rotate-left-6, shift-1: My super secret string
^C^C^C
```

We can then stop the research with Ctrl+C. The right output has been found !

