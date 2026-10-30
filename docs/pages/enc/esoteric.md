`codext` also implements esoteric programming languages: encoding generates a program that prints the text, while decoding runs the program and returns its output. Programs are run by a sandboxed interpreter: they have no input, and they are stopped when they do not halt within a number of steps.

-----

### Befunge

Befunge-93 programs are grids of 80x25 cells (wrapping around on the edges) where an instruction pointer moves in four directions, working on a stack of integers. Encoding generates an ASCII program that pushes the text (in string mode for printable characters, as small arithmetic expressions for the other bytes) and prints it in a loop, with rows of 80 cells snaking downward. Programs are run as with the [reference interpreter](https://github.com/catseye/Befunge-93), cells holding signed characters.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`befunge` | text <-> Befunge-93 program | `befunge93`, `befunge-93` | programs read as UTF-8 ; executing an unsupported instruction only accepted with a non-strict errors handling ; programs that do not halt within 1000 steps per instruction (with a minimum of 1 million) are stopped

!!! note "Deviations from the reference interpreter"

    Without input, `&` and `~` push -1. A division or a modulo by zero gives 0 (the reference interpreter asks the user). `?` uses a seeded pseudo-random generator, so that decoding is reproducible. The playfield is extended for programs larger than 80x25, e.g. those generated for long texts, which the reference interpreter would truncate.

```python
>>> codext.encode("Hello, World!", "befunge")
'"!dlroW ,olleH">:#,_@'
>>> codext.decode('                 v\n>v"Hello world!"0<\n,:\n^_25*,@', "befunge")
'Hello world!\n'
```

-----

### Brainfuck

[Brainfuck](https://esolangs.org/wiki/Brainfuck) is an esoteric programming language working on a tape of 8-bit cells with 8 commands: `+` and `-` (increment and decrement the cell), `>` and `<` (move the pointer), `[` and `]` (loop while the cell is not null), `.` (output the cell) and `,` (input a byte). Encoding generates a program that prints the text (as UTF-8), while decoding runs the program (with no input) and returns its output.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`brainfuck` | text <-> Brainfuck program | `brainf*ck`, `bf` | whitespace ignored ; other characters (comments) only accepted with a non-strict errors handling ; programs that do not halt within 1000 steps per command (with a minimum of 1 million) are stopped

```python
>>> codext.encode("Hi", "brainfuck")
'>++++++++[<+++++++++>-]<.>++++[<++++++++>-]<+.'
>>> codext.decode("++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++.", "bf")
'Hello World!\n'
>>> codext.decode("Prints A: ++++++++[>++++++++<-]>+.", "brainfuck", "ignore")
'A'
```

-----

### Church

[Church encoding](https://en.wikipedia.org/wiki/Church_encoding) represents data in the untyped [lambda calculus](https://en.wikipedia.org/wiki/Lambda_calculus), whose terms are variables, abstractions (`\x.M` or `λx.M`, a function of `x`) and applications (`M N`). The natural number *n* is the numeral `\f.\x.f (f ... (f x))`, applying `f` *n* times to `x`, and the list `[a, b, ...]` is its right fold `\c.\n.c a (c b (... n))`. Encoding generates a program that evaluates to the list of the numerals of the bytes of the text (as UTF-8), while decoding evaluates the program and returns the bytes of the list it gives.

The program is a single term: abstractions extend as far to the right as possible, applications are left-associative and `\x y.M` stands for `\x.\y.M`. It is evaluated lazily in normal order (call-by-need), so that only the list and its numerals are reduced, and must give a list of numerals lower than 256.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`church` | text <-> lambda term of a Church list of Church numerals | `church-encoding`, `lambda-calculus` | variables made of letters, digits, `_` and `'` (not starting with a digit), and bound ; syntax and evaluation errors reported whatever the errors handling ; programs that do not give their list within 1000 steps per token (with a minimum of 1 million) are stopped

```python
>>> codext.encode("\x01\x02", "church")
'\\c.\\n.c (\\f.\\x.f x) (c (\\f.\\x.f (f x)) n)'
>>> mult, n8, n9 = r"(\m n f.m (n f))", r"(\f x.f (f (f (f (f (f (f (f x))))))))", r"(\f x.f (f (f (f (f (f (f (f (f x)))))))))"
>>> codext.decode(rf"\c n.c ({mult} {n8} {n9}) n", "church")
'H'
```

-----

### COW

COW is made of 12 variations of the word "moo". Its memory is a tape of integer cells with a register, and its instructions include those of Brainfuck (`MoO`, `MOo`, `moO`, `mOo`, `MOO`, `moo`, `Moo`), plus integer output and input (`OOM`, `oom`), reset (`OOO`), copy and paste through the register (`MMM`) and the execution of the value of the cell as an instruction (`mOO`). Programs are run as with the reference interpreter, including the quirks of its loops: when searching for their match, `MOO` skips the instruction that follows it and `moo` the one that precedes it.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`cow` | text <-> COW program | | instructions are case-sensitive ; whitespace ignored ; other characters (comments) only accepted with a non-strict errors handling ; programs that do not halt within 1000 steps per instruction (with a minimum of 1 million) are stopped

```python
>>> codext.encode("A", "cow")
'moO MoO MoO MoO MoO MoO MoO MoO MoO MOO mOo MoO MoO MoO MoO MoO MoO MoO MoO moO MOo moo mOo MoO Moo'
>>> codext.decode("MoO MoO MOO MOo moO MoO mOo moo moO OOM", "cow")
'2\n'
```

-----

### LOLCODE

[LOLCODE](https://esolangs.org/wiki/LOLCODE) programs start with `HAI` and end with `KTHXBYE`, and work on dynamically typed variables (`I HAS A <var> ITZ <value>`, `<var> R <value>`) holding untyped values (`NOOB`), booleans (`WIN` and `FAIL`), integers, floats or strings (with escapes such as `:)` for a newline). The language has prefix operators (`SUM OF <x> AN <y>`, `BOTH SAEM <x> AN <y>`, `SMOOSH <x> AN <y> MKAY`, ...), conditionals (`O RLY?` and `WTF?`), loops (`IM IN YR <label> ... IM OUTTA YR <label>`) and functions (`HOW IZ I <name> ... IF U SAY SO`), and prints with `VISIBLE` (with a newline, unless ended with `!`). Encoding generates an ASCII program with one `VISIBLE` per line of the text. Programs are run according to the [1.2 specification](https://github.com/justinmeza/lolcode-spec/blob/master/v1.2/lolcode-spec-v1.2.md), with the behavior of the [reference interpreter](https://github.com/justinmeza/lci) (lci) where the specification says nothing.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`lolcode` | text <-> LOLCODE program | `lol` | syntax and runtime errors reported whatever the errors handling ; programs that do not halt within 1000 steps per token (with a minimum of 1 million) are stopped
`lolcode-lower` | text <-> LOLCODE program with lowercase keywords | `lol_lower`, `lolcode-lowercase` | also decodes uppercase keywords ; lowercase keywords (e.g. `i` or `a`) cannot be used as identifiers

!!! note "Differences with the reference interpreter"

    Features of LOLCODE 1.3 (`BUKKIT` arrays, `SRS`, `'Z`, ...) are not supported. Without input, `GIMMEH` gives an empty string. The version after `HAI` is optional (as in former versions of the language). As in the specification, variables have the scope of the main program or of the function (instead of the block), and casting a string that is not a number (e.g. `"abc"` or `" 12"`) to a number is an error (lci gives 0 or parses it leniently). `WIN` and `FAIL` are printed as such (lci reports an error).

```python
>>> codext.encode("Hello\nWorld!", "lolcode")
'HAI 1.2\nVISIBLE "Hello"\nVISIBLE "World!"!\nKTHXBYE'
>>> codext.encode("Hello\nWorld!", "lolcode-lower")
'hai 1.2\nvisible "Hello"\nvisible "World!"!\nkthxbye'
>>> codext.decode('HAI 1.2\nIM IN YR loop UPPIN YR n TIL BOTH SAEM n AN 3\n  VISIBLE "KTHX " SUM OF n AN 1\nIM OUTTA YR loop\nKTHXBYE', "lolcode")
'KTHX 1\nKTHX 2\nKTHX 3\n'
```

-----

### Malbolge

[Malbolge](https://esolangs.org/wiki/Malbolge) is an esoteric programming language designed to be as difficult to program in as possible. It runs on a ternary virtual machine with 59049 words of 10 trits, holding both the code and the data, and three registers (`A`, the accumulator, `C`, the code pointer, and `D`, the data pointer). The instruction executed depends on the character at `C` and on its position, among `j` (`D = [D]`), `i` (`C = [D]`), `*` (rotate `[D]` to the right), `p` ("crazy" tritwise operation of `A` and `[D]`), `<` (output `A`), `/` (input to `A`), `v` (stop) and `o` (nop), and the executed character is then enciphered. Encoding generates a program that prints the text (as UTF-8), searching for each byte the shortest sequence of instructions setting `A` to it, while decoding runs the program and returns its output. Programs are run as with the [reference interpreter](https://www.lscheffer.com/malbolge_interp.html) (`<` being the output), the cases it leaves undefined being handled as in the [specification](https://www.lscheffer.com/malbolge_spec.html).

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`malbolge` | text <-> Malbolge program | `mb` | at least two instructions ; whitespace ignored ; invalid characters only accepted with a non-strict errors handling ; programs that do not halt within 1000 steps per instruction (with a minimum of 1 million) are stopped

!!! note "Undefined behaviors"

    Executing a character that is not graphic ASCII ends the program, and a modified cell that is no longer graphic ASCII is not enciphered. Without input, `/` gives the end of file (59048).

```python
>>> codext.encode("Hi", "malbolge")
'DCBA@?>=6;:981U543210/.-&%*#G4'
>>> codext.decode("(=<`#9]~6ZY32Vx/4Rs+0No-&Jk)\"Fh}|Bcy?`=*z]Kw%oG4UUS0/@-ejc(:'8dc", "mb")
'Hello World!'
```

-----

### Ook!

[Ook!](https://www.dangermouse.net/esoteric/ook.html) is an esoteric programming language derived from Brainfuck, designed to be read and written by orang-utans: each Brainfuck command is a pair of the words `Ook.`, `Ook?` and `Ook!` (e.g. `Ook. Ook?` for `>` and `Ook! Ook.` for `.`). Short Ook! only keeps the punctuation marks (e.g. `.?` for `>`). Encoding generates a program that prints the text (as UTF-8), while decoding runs the program (with 8-bit cells and no input) and returns its output.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`ook` | text <-> Ook! program | `ook!`, `ook-short`, `short-ook` | both forms decoded (case-insensitive) ; whitespace ignored ; other characters only accepted with a non-strict errors handling ; programs that do not halt within 1000 steps per command (with a minimum of 1 million) are stopped

```python
>>> codext.encode("A", "ook-short")
'.?................!??..................?!!?!?...!.'
>>> codext.decode(".?................!??..................?!!?!?...!.", "ook")
'A'
>>> codext.decode("Ook. Ook. Ook. Ook. Ook! Ook.", "ook")
'\x02'
```

-----

### Piet

[Piet](https://www.dangermouse.net/esoteric/piet.html) programs are images looking like abstract paintings, made of codels (squares of pixels) of 20 colors: 18 colors of 6 hues in 3 lightnesses, white and black. Connected codels of the same color form color blocks, through which the interpreter moves according to a direction pointer and a codel chooser, sliding through white codels and being blocked by black codels and the edges ; it halts when it cannot leave a block. Moving from a block to another executes a command on a stack of integers, given by the change of hue and lightness (e.g. one step darker pushes the size of the block, five hues and two steps darker prints a character). Encoding generates a PNG image of a program that prints the text, while decoding reads a PNG, GIF or PPM image and runs the program, returning its output.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`piet` | text <-> Piet program (image) | `piet-N` (*N* being the codel size) | codel size 1 by default when encoding, guessed when decoding ; other colors only accepted (as white) with a non-strict errors handling ; programs that do not halt within 1000 steps per color block (with a minimum of 1 million) are stopped

!!! note "Implementation choices"

    Without input, `in(number)` and `in(char)` are ignored, as are the commands that cannot be performed (e.g. popping an empty stack or dividing by zero). Division rounds towards negative infinity and `mod` has the sign of the divisor. `out(char)` prints the character of the Unicode code point (the [npiet](https://www.bertnase.de/npiet/) interpreter only prints its lowest byte), so that the generated programs push code points rather than UTF-8 bytes.

```python
>>> png = codext.encode(b"Hello World!", "piet-10")
>>> png[:8]
b'\x89PNG\r\n\x1a\n'
>>> codext.decode(png, "piet")
b'Hello World!'
>>> codext.decode("P3 4 2 255\n255 192 192  255 0 0  192 0 192  255 0 255\n255 192 192  0 0 0  255 0 255  255 0 255\n", "piet")
'2'
```

-----

### Pikalang

[Pikalang](https://github.com/groteworld/pikalang) is an esoteric programming language derived from Brainfuck, using the vocabulary of Pikachu: `pi` (`+`), `ka` (`-`), `pipi` (`>`), `pichu` (`<`), `pika` (`[`), `chu` (`]`), `pikachu` (`.`) and `pikapi` (`,`). Encoding generates a program that prints the text (as UTF-8), while decoding runs the program (with 8-bit cells and no input) and returns its output.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`pikalang` | text <-> Pikalang program | | words separated by whitespace ; programs that do not halt within 1000 steps per word (with a minimum of 1 million) are stopped

```python
>>> codext.encode("Hi", "pikalang")
'pipi pi pi pi pi pi pi pi pi pika pichu pi pi pi pi pi pi pi pi pi pipi ka chu pichu pikachu pipi pi pi pi pi pika pichu pi pi pi pi pi pi pi pi pipi ka chu pichu pi pikachu'
>>> codext.decode("pi pi pi pi pi pi pi pi pika pipi pi pi pi pi pi pi pi pi pichu ka chu pipi pi pikachu", "pikalang")
'A'
```
