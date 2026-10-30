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
