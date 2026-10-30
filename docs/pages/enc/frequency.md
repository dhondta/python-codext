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

-----

### Piccolo

[Piccolo](https://www.cryptomuseum.com/ref/piccolo/index.htm) is an MFSK system used by the British Diplomatic Wireless Service (DWS) since 1962, sending the characters of the ITA-2 (Baudot) code as audio tones. Piccolo I sends each code as one of 32 tones, from 460 Hz (code 0) to 770 Hz (code 31), every 10 Hz. Piccolo II (aka Piccolo Mk 6) sends each code as a sequence of two tones of 50 ms, out of 6 tones (A to F) from 460 to 560 Hz, every 20 Hz : of the 36 pairs, DE and ED are used for synchronisation, EE for multiple identification and DD is not used. Piccolo III sends the same pairs as Piccolo II, with 6 tones from 1900 to 2100 Hz, every 40 Hz. As with ITA-2, the LTR and FIG codes switch between the letters and the figures shifts.

**Codec** | **Conversions** | **Aliases** | **Comment**
:---: | :---: | --- | ---
`piccolo` | text <-> Piccolo tones (Hz) | `piccolo1`, `piccolo-ii`, `piccolo_mk6`, `piccolo-iii`, ... | parametrized ; *variant* belongs to {1 (I), 2 (II, Mk6), 3 (III)} (default: 2) ; letters uppercased ; letters shift assumed at the start ; synchronisation and identification pairs ignored when decoding

!!! note "Character set"

    As with [Coquelet](#coquelet), the figures shift follows ITA-2, except for `;` instead of `=`. The 12-tone version of Piccolo II for ITA-5 (7-bit ASCII, aka Piccolo Mk 12) is not implemented, as its character table is not documented.

```python
>>> codext.encode("SOS 123", "piccolo")
'460 540 560 460 460 540 460 520 560 560 520 560 500 560 460 480'
>>> codext.encode("SOS 123", "piccolo-i")
'510 700 510 500 730 690 650 470'
>>> codext.encode("SOS 123", "piccolo-iii")
'1900 2060 2100 1900 1900 2060 1900 2020 2100 2100 2020 2100 1980 2100 1900 1940'
>>> codext.decode("520 540 500 460 540 520 460 480", "piccolo")
'TE'
```
