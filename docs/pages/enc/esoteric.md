`codext` also implements esoteric programming languages: encoding generates a program that prints the text, while decoding runs the program and returns its output. Programs are run by a sandboxed interpreter: they have no input, and they are stopped when they do not halt within a number of steps.

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
