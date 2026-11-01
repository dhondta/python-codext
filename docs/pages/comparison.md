`codext` is not the only tool for encoding and decoding data, nor for guessing how data was encoded. This page compares it with three popular tools, [CyberChef](https://github.com/gchq/CyberChef), [Ciphey](https://github.com/bee-san/Ciphey) and [dCode](https://www.dcode.fr), so as to help choosing the right one for a task.

!!! note "Snapshot"

    The figures below were gathered in November 2026 (codext 2.0.1, CyberChef 11.5.0, Ciphey 0.12.0 on crates.io with its repository as of November 2026, dCode as online) ; they evolve with each project.

-----

### Summary

| | codext | CyberChef | Ciphey | dCode |
|---|---|---|---|---|
| Form | Python library and CLI tools | Web application (also downloadable to run offline) and Node.js package | CLI tool and Rust library (also an MCP server and a Discord bot) | Website |
| Programmatic use | Yes, from Python, through the native `codecs` module (`codecs.encode`, `codecs.open`, ...) | Yes, from Node.js (`npm install cyberchef`, `chef.bake(...)`), except flow control operations | Yes, from Rust ; the former Python version (5.14.0, June 2021) is no longer maintained | No (no public API, closed source) |
| Works offline | Yes | Yes | Yes | No |
| License | GPL-3.0 | Apache-2.0 | MIT | Proprietary |
| Size | 283 codecs (and 92 native Python codecs) in 15 categories, most of them with variants (e.g. `rot-1` to `rot-25`) ; 1279 encodings tried while guessing | 506 operations (encoding and decoding counted separately), of which about 300 for data formats, encodings, encryption, compression and hashing | 82 decoders | Over 900 tools (ciphers, but also mathematics, games and puzzles) |
| Encodes and decodes | Both, with every codec | Both | Decodes only | Both, for most tools |
| Automatic decoding of multiple layers | Yes: `guess`, a breadth-first search ordered by a ranking heuristic, with stop functions (text, flag, regex, natural language) and bounds (timeout, number of nodes, beam) | Yes: the *Magic* operation, which detects encodings with regular expressions, tries them and scores the outputs (magic bytes, UTF-8 validity, entropy, letter frequencies), up to a given depth | Yes: an A* search over its decoders, stopping at the first output that its checkers (English, regex cribs, known patterns, ...) consider as a plaintext | No: the *cipher identifier* (statistics and a neural network) suggests which tools to use, one layer at a time |
| Keyed ciphers without the key | Only the keys tried while guessing (e.g. `vigenere-key`, `vigenere-password`) | Single-byte XOR and bit rotations (*Magic* in intensive mode) | Yes, with crackers (e.g. Caesar, Vigenère, repeating-key XOR, monoalphabetic substitution) | Yes, for many classical ciphers (e.g. the Kasiski test for Vigenère) |
| Ranking of the candidate decodings | Yes (`rank`, `codext rank`) | No | No | Yes, for the identified ciphers |
| Strength of a chain of codecs | Yes (`strength`) and composition of a strong chain from assessment questions (`compose`) | No | No | No |
| Extensibility | New codecs from functions or character maps (`add`, `add_map`), macros (chains of codecs) | Recipes (chains of operations) ; new operations by contributing | New decoders by contributing | None |

-----

### How to read the figures

The counts are not directly comparable, as each tool counts different things:

- a codext **codec** usually holds several **encodings** (e.g. the `base32` codec holds `base32`, `base32-hex`, `base32-crockford`, ...) and both encodes and decodes ;
- a CyberChef **operation** works in one direction (e.g. *To Base64* and *From Base64*), and many operations are not encodings (e.g. networking, date and time, code beautifiers) ;
- a Ciphey **decoder** only decodes, but some of them crack a whole family of ciphers without the key ;
- a dCode **tool** can be a cipher, but also a calculator or a puzzle solver.

-----

### Strengths of each tool

- **codext** integrates with Python itself: once imported, its codecs are available through the native `codecs` module, including for reading and writing files. It encodes as well as it decodes, ranks the candidate decodings, and can evaluate and compose chains of codecs that resist guessing. It does not cover modern cryptography (e.g. AES, RSA) nor cryptanalysis of keyed ciphers.
- **CyberChef** offers the broadest set of data manipulations beyond encodings (encryption, networking, forensics, multimedia) in a graphical interface where recipes are built by drag and drop, also usable from Node.js.
- **Ciphey** focuses on decoding without any knowledge, including cracking keyed classical ciphers, and stops as soon as an output looks like a plaintext.
- **dCode** covers the largest number of classical ciphers, with detailed explanations and solvers, but only online and one tool at a time.

-----

### Sources

- CyberChef: [repository](https://github.com/gchq/CyberChef), [list of operations](https://github.com/gchq/CyberChef/blob/master/src/core/config/Categories.json), [Magic](https://github.com/gchq/CyberChef/wiki/Automatic-detection-of-encoded-data-using-CyberChef-Magic), [Node API](https://github.com/gchq/CyberChef/wiki/Node-API)
- Ciphey: [repository](https://github.com/bee-san/Ciphey) (formerly Ares, the Rust rewrite of Ciphey), [decoders](https://github.com/bee-san/Ciphey/tree/master/src/decoders), [crate](https://crates.io/crates/ciphey), [former Python version](https://pypi.org/project/ciphey/)
- dCode: [website](https://www.dcode.fr/en), [cipher identifier](https://www.dcode.fr/cipher-identifier)
- codext: counted from its registry (`codext.list_encodings()` and the codecs' parameters)
