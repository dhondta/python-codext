## Frequency

`codext` also implements radio teleprinter systems that send characters as audio tones (Multi Frequency-Shift Keying, MFSK) : encoding gives the frequencies of the tones in Hz, while decoding gives back the text.

-----

### Coquelet

[Coquelet](https://www.cryptomuseum.com/ref/coquelet/index.htm) is an MFSK system developed by ACEC in Belgium in the 1950s, used by the armies and police services of Belgium, France, Algeria and other countries. With Coquelet 13 (Mk 1), each character of the ITA-2 (Baudot) code is sent as two tones of 75 ms: the first one, out of the 8 tones of Group I (812 to 1022 Hz, every 30 Hz), gives its bits 3 to 5, while the second one, out of the 4 tones of Group II (1082 to 1172 Hz), gives its bits 1 and 2. A 1052 Hz tone is sent when idle. As with ITA-2, the LTR and FIG codes switch between the letters and the figures shifts.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`coquelet` | text <-> Coquelet 13 tones (Hz) | `coquelet13`, `coquelet-13`, `coquelet-mk1` | letters uppercased ; letters shift assumed at the start ; idle tones ignored when decoding

!!! note "Character set"

    The figures shift follows ITA-2, except for `;` instead of `=` (as with US teleprinters). Coquelet 8 (Mk 2) is not implemented, as its character table is not documented.

```python
>>> codext.encode("SOS 123", "coquelet")
'902 1112 842 1172 902 1112 902 1172 842 1082 932 1082 872 1082 1022 1112'
>>> codext.decode("1052 872 1172 1052 1022 1112", "coquelet")
'TE'
```
