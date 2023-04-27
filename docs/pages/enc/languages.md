`codext` also adds some common languages for encoding.

-----

### Braille

It supports letters, digits and some special characters.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`braille` | text <-> braille symbols | | Python 3 only

```python
>>> codext.encode("this is a test", "braille")
'⠞⠓⠊⠎⠀⠊⠎⠀⠁⠀⠞⠑⠎⠞'
>>> codext.encode("THIS IS A TEST", "braille")
'⠞⠓⠊⠎⠀⠊⠎⠀⠁⠀⠞⠑⠎⠞'
>>> codext.decode("⠞⠓⠊⠎⠀⠊⠎⠀⠁⠀⠞⠑⠎⠞", "braille")
'this is a test'
```

-----

### Galactic

This implements the [Minecraft's enchanting table](https://www.thegamer.com/minecraft-enchantment-table-language-guide/) using resembling Unicode characters.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`galactic` | text <-> Minecraft enchantment symbols | `galactic-alphabet`, `minecraft_enchantment`, `minecraft-enchanting-language` | Python 3 only

```python
>>> codext.encode("this is a test", "galactic")
'ℸ₸╎߆ ╎߆ ᒋ ℸᒷ߆ℸ'
>>> codext.decode("ℸ₸╎߆ ╎߆ ᒋ ℸᒷ߆ℸ", "galactic")
'this is a test'
```

-----

### Ipsum

This implements a codec that uses lorem ipsum words. It selects random words per letter and keeps the following punctuations: "`.,:;+=-*/\\`".

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`ipsum` | text <-> latin words | `loremipsum`, `lorem-ipsum` | words from the classical lorem ipsum

```python
>>> codext.encode("This is a test.", "ipsum")
'Torquent hystericus id sit  interdum sit  aliquam  tempor erat scelerisque taciti.'
>>> codext.decode("Torquent hystericus id sit  interdum sit  aliquam  tempor erat scelerisque taciti.", "lorem-ipsum")
'This is a test.'
```

-----

### Leetspeak

This implements a very basic ruleset of elite speaking.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`leetspeak` | text <-> leetspeak encoded text | `leet`, `1337`, `leetspeak` | based on minimalistic elite speaking rules

```python
>>> codext.encode("this is a test", "leetspeak")
'7h15 15 4 7357'
>>> codext.decode("7h15 15 4 7357", "leetspeak")
'ThIS IS A TEST'
```

-----

### Morse

It supports of course letters and digits, but also a few special characters: `.,;:?!/\\@&=-_'" $()`.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`morse` | text <-> morse encoded text | none | uses whitespace as a separator, dynamic tokens mapping ; we can define a mapping of encoding's tokens (original tokens: `/-.`)

```python
>>> codext.encode("this is a test", "morse")
'- .... .. ... / .. ... / .- / - . ... -'
>>> codext.encode("this is a test", "morse/-.")
'- .... .. ... / .. ... / .- / - . ... -'
>>> codext.encode("this is a test", "morse_ABC")
'B CCCC CC CCC A CC CCC A CB A B C CCC B'
>>> codext.decode("- .... .. ... / .. ... / .- / - . ... -", "morse")
'this is a test'
>>> with codext.open("morse.txt", 'w', encoding="morse") as f:
	f.write("this is a test")
14
>>> with codext.open("morse.txt", encoding="morse") as f:
	f.read()
'this is a test'
```

-----

### Navajo

It implements the letters from the [Navajo Code Talkers' Dictionary](https://www.history.navy.mil/research/library/online-reading-room/title-list-alphabetically/n/navajo-code-talker-dictionary.html). It conserves digits and newlines.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`navajo` | text <-> Navajo | | 

```python
>>> import codext
>>> codext.encode("this is a test 123", "navajo")
'a-woh cha tkin klesh - a-chi klesh - be-la-sana - a-woh dzeh klesh a-woh - 1 2 3'
>>> codext.decode("a-woh cha tkin klesh - a-chi klesh - be-la-sana - a-woh dzeh klesh a-woh - 1 2 3", "navajo")
'this is a test 123'
```

-----

### Radio Alphabet

This is also known as the [NATO phonetic alphabet](https://en.wikipedia.org/wiki/NATO_phonetic_alphabet).

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`radio` | text <-> radio alphabet words | `military_alphabet`, `nato-phonetic-alphabet`, `radio-alphabet` | 

```python
>>> codext.encode("foobar", "nato_phonetic_alphabet")
'Foxtrot Oscar Oscar Bravo Alpha Romeo'
>>> codext.decode("Foxtrot Oscar Oscar Bravo Alpha Romeo", "radio-alphabet")
'FOOBAR'
```

-----

### Southpark

This encodes text according to Kenny's language in Southpark.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`southpark` | text <-> Kenny's language | `kenny` | Dynamic tokens mapping ; we can define a mapping of encoding's tokens (original tokens: `fFMmpP`)
`southpark-icase` | text <-> Kenny's language | `kenny_icase` | Dynamic tokens mapping ; we can define a mapping of encoding's tokens (original tokens: `FMP`)

```python
>>> codext.encode("This is a Test", "southpark")
'FmpmfpmfffmmfffmfffmmfffmmmfffFmpmppfmmfmp'
>>> codext.decode('FmpmfpmfffmmfffmfffmmfffmmmfffFmpmppfmmfmp', "kenny")
'This is a Test'
>>> codext.encode("This is a test", "kenny_123456")
'245415411144111411144211444111145455144145'
>>> codext.decode("245415411144111411144211444111145455144145", "kenny-123456")
'This is a test'
>>> codext.encode("this is a test", "kenny_icase")
'FMPMFPMFFFMMFFFMFFFMMFFFMMMFFFFMPMPPFMMFMP'
>>> codext.decode("FMPMFPMFFFMMFFFMFFFMMFFFMMMFFFFMPMPPFMMFMP", "southpark-icase")
'this is a test'
>>> codext.encode("this is a test", "southpark-icase_123")
'123213211122111211122111222111123233122123'
>>> codext.decode('123213211122111211122111222111123233122123', "kenny_icase-123")
'this is a test'
```

-----

### Tap

This codec implements the [tap/knock code](https://en.wikipedia.org/wiki/Tap_code) commonly used by prisoners. It uses 25 letters, "*k*" is encoded to the same token than "*c*".  

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`tap` | text <-> tap/knock encoded text | `knock`, `tap-code` | uses a large Unicode whitespace as a token separator ; Python 3 only

```python
>>> codext.encode("this is a test", "tap")
'.... ....⠀.. ...⠀.. ....⠀.... ...⠀ ⠀.. ....⠀.... ...⠀ ⠀. .⠀ ⠀.... ....⠀. .....⠀.... ...⠀.... ....'
>>> codext.decode(".... ....⠀.. ...⠀.. ....⠀.... ...⠀ ⠀.. ....⠀.... ...⠀ ⠀. .⠀ ⠀.... ....⠀. .....⠀.... ...⠀.... ....", "knock")
'this is a test'
```

-----

### Tom-Tom

This codec is similar to morse. It converts text into slashes and backslashes.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`tomtom` | text <-> tom-tom encoded text | `tom-tom` | uses "`|`" as a separator

```python
>>> codext.encode("this is a test", "tom-tom")
'\\\\/\\ /\\\\ /\\\\\\ \\/\\ | /\\\\\\ \\/\\ | / | \\\\/\\ /\\ \\/\\ \\\\/\\'
>>> codext.decode("\\\\/\\ /\\\\ /\\\\\\ \\/\\ | /\\\\\\ \\/\\ | / | \\\\/\\ /\\ \\/\\ \\\\/\\", "tomtom")
'THIS IS A TEST'
```
