Besides the [guess mode](guessing.md), which tries to reverse an unknown chain of encodings, `codext` can analyze an input, to tell what it may be before trying to decode it, and crack a keyed cipher whose key is unknown. Both features are inspired by [FeatherDuster](https://github.com/nccgroup/featherduster) and are independent of the guess mode, which does not use them.

-----

### Analysis

`analyze` reports the statistical properties of an input (`str` or `bytes`), with human-readable hints:

```python
>>> import codext
>>> r = codext.analyze("5d41402abc4b2a76b9719d911017c592")
>>> r['alphabet'], r['hashes']
('hexadecimal', 'MD4, MD5, NTLM')
>>> r['hints']
['It has the length of a hash digest (MD4, MD5, NTLM)', 'It only holds hexadecimal characters, hence it may be encoded with it']
```

The properties are:

| Property | Description |
| :--- | :--- |
| `length` | Length in bytes (a `str` being taken as UTF-8) |
| `alphabet` | Smallest known alphabet holding all the characters, whitespaces ignored (e.g. `binary digits`, `hexadecimal`, `Base32`, `Base64`, `printable characters`), or `None` |
| `printables` | Rate of printable characters |
| `entropy` | Shannon entropy of the bytes, in bits per byte (8 at most) |
| `mean` | Mean of the bytes (127.5 for random data) |
| `chi_square` | Chi-square of the distribution of the bytes (close to 255 for random data) |
| `compression_ratio` | Length of the zlib compression divided by the length (close to or above 1 for random data) |
| `longest_bit_run` | Length of the longest run of identical bits |
| `monte_carlo_pi` | Monte Carlo estimate of Pi from the bytes (close to Pi for random data, as with the `ent` tool) |
| `signature` | Format of the file signature the input starts with (e.g. `gzip`, `PNG`, `OpenSSL encrypted data`), or `None` |
| `hashes` | Hashes whose digest has the length of the input (in bytes, or in hexadecimal characters), or `None` |
| `repeated_blocks` | Numbers of repeated blocks by block size (8 or 16 bytes, when the length is a multiple of it), as a block cipher in ECB mode gives for repeated plaintext blocks |
| `letters` | Number of Latin letters |
| `index_of_coincidence` | Probability that two letters are equal (.0667 for English texts, .0385 for random letters) |
| `letter_shift` | Shift N whose decoding (`rot-N`) distributes the letters the most as in a text, with how well they then fit the letter frequencies of a text (from 0 to 1, random letters fitting around .6) |
| `key_length` | Estimated key length of a polyalphabetic substitution of the letters (e.g. Vigenère), or `None` |
| `textness` | How much the input looks like a natural language text (from 0 to 1, as rated by the guess mode) |
| `hints` | Human-readable interpretations of these properties |

For a ciphertext mostly made of letters, the hints tell the kind of classical cipher from the index of coincidence and the letter frequencies: a transposition (the letters are distributed as in a text but do not form words), a Caesar cipher (they are, once shifted), another monoalphabetic substitution (the index of coincidence is the one of a text, but no shift fits) or a polyalphabetic substitution (the letters are evenly distributed), with its likely key length. For binary data, they tell whether it looks random, that is, encrypted, random or compressed without a header: guessing an encoding is then unlikely to help.

From the terminal, the input is given with `-i` or through a pipe:

```session
$ echo -en "It was a bright cold day in April, ..." | codext encode vigenere-rainbow | codext analyze
length               : 310
alphabet             : printable characters
[...]
index of coincidence : 0.0395
letter shift         : rot-8 (fit: 0.66)
key length           : 7
textness             : 0.2051

[*] Its letters are evenly distributed, as with a polyalphabetic substitution (e.g. vigenere) whose key would be 7 letters long.
```

-----

### Cracking

`crack` recovers the most likely keys of a cipher for a ciphertext, decodes the ciphertext with each of them and ranks the outputs by how much they look like a text. It returns a list of `(score, encoding, output)` tuples, from the best score (1 at most):

```python
>>> codext.crack("rglpxoiodltueosefdomerndat", "columnar", 2)
[(0.8666666666666666, 'columnar-23541', 'ourfriendgoodoldsampletext'), (0.8249999999999998, 'columnar-25341', 'orufrinedgodooldasmplteext')]
>>> codext.crack("SpTtmexale", "skip", 1)
[(1.0, 'skip-3', 'SampleText')]
```

| Cipher | Key recovery |
| :--- | :--- |
| `vigenere`, `beaufort`, `gronsfeld` | For each key length (up to 20 letters by default), each key letter is the shift of the corresponding letters (taken every key length letters) that distributes them the most as in a text ; the best keys are then refined letter by letter with the trigrams of the whole output |
| `vernam` (repeating-key XOR) | The most likely key sizes (up to 32 characters by default) are the ones whose successive blocks are the closest in Hamming distance ; for each of them, each key character is the one that makes the corresponding characters look the most as a text |
| `columnar` | All the orders of the columns are tried (brute force, up to 7 columns by default, i.e. 5913 orders), keeping the orders whose outputs hold the most common English trigrams |
| any other codec | The encodings it lists for the guess mode are tried and ranked (e.g. `railfence-1` to `railfence-10`, `rot-1` to `rot-25`, `skip-1` to `skip-8`) |

The score is the mean of the textness of the output (as rated by the guess mode) and of the frequency of its trigrams in English texts (only the latter for an output without spaces, as the textness relies on words), weighted by the fit of its letter frequencies.

`crack` accepts the following arguments:

- `limit`: maximum number of results (10 by default ; all of them if `None` or negative)
- `max_key_length`: maximum key length (in letters, characters or columns, depending on the cipher)
- `timeout`: maximum duration of the key search in seconds, then using the keys found so far

```session
$ codext -i ciphertext.txt crack vigenere -l 2
[+] 0.94140: vigenere-rainbow
    It was a bright cold day in April, and the clocks were striking thirteen....
[+] 0.39865: vigenere-umfwrzpiharqxtmf
    Fh zrc p iabode trqy rbu as Sarom, xtx adm jnfxtb uxya sdcczrpl otetsson....
```

With `-o`, the best output is written to the given file. Once the key is known, the encoding can also be given to the guess mode, e.g. `codext guess -i vigenere-rainbow`, for decoding the other layers.

!!! warning "Statistical attacks need enough ciphertext"

    The key recovery relies on statistics, hence it needs enough ciphertext: a few tens of letters per key letter for a polyalphabetic substitution, a few blocks of the key size for repeating-key XOR. On a short ciphertext (e.g. "Jour toiglm cmoeetmku.", from `vigenere-rainbow`), the best output is a plausible-looking but wrong decoding. The trigrams are those of English texts, hence a text in another language gets lower scores.

!!! note "Not used by the guess mode"

    Cracking runs only on request, for a given cipher: the guess mode keeps trying its fixed list of keys (e.g. `vigenere-key`, `vigenere-password`), as cracking every cipher at every step of its search would slow it down.
