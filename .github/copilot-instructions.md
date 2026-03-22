# Copilot Instructions — Enhancements Only

## Scope
This repository focuses on **adding new encoding/decoding schemes only**.

Copilot MUST:
- Propose **new codecs only**
- Avoid refactoring unrelated code
- Avoid dependency changes unless strictly required for the codec
- Avoid stylistic or formatting changes

## Context
This project extends Python's codecs with many encoding/decoding schemes and a CLI tool.
It already includes a wide variety of bases, ciphers, compression, and niche encodings.

## Enhancement Guidelines
When adding a new encoding, follow the guideline in the documentation at `docs/pages/howto.md`.


## Implementation Constraints

- Pure Python preferred
- No heavy dependencies
- Deterministic transformations only
- Reversible encoding required unless explicitly documented

## Testing

Every new codec:
- SHOULD include a list of `__examples__` that tells the automated tests what encoding/decoding transformations need to be verified ; it this cannot be made, unit tests (encode/decode roundtrip) SHALL be provided in `tests/test_manual.py`
- Edge cases (empty input, binary data if applicable), either in the `__examples__` list or in the explicit tests in `tests/test_manual.py`

## Documentation

Each codec SHALL comply with the following structure:

    ```python
    # -*- coding: UTF-8 -*-
    """{{codec_long_name}} Codec - {{codec_short_name}} content encoding.

    {{codec_description}}

    This codec:
    - en/decodes strings from str to str
    - en/decodes strings from bytes to bytes
    - decodes file content to str (read)
    - encodes file content from str to bytes (write)

    Reference: {{codec_source_hyperlink}}
    """
    from ..__common__ import *


    __examples__ = {<<dictionary of examples with, as keys, a special format detailed hereafter and, as values, a dictionary mapping source to destination values (see sectino _Self-generated tests_)>>}
    <<optional list of valid codec names to be used with the guessing mode (see _Codec names for the guessing mode_), in format "__guess__ = [...]">>]


    <<constants here, including ENCMAP if the codec is a simple mapping (see section _Case 2: Encoding map_)>>
    <<functions here, if the codec requires some additional logic, i.e. when it is not a mapping (see section _Case 1: Generic encoding definition_)>>


    <<put the right add function (see section _Which `add` function ?_) here with its relevant parameters (see section _Generic arguments_)>>
    ```

In this template, `{{ ... }}` enclosures indicate codec's properties and `<< ... >>``enclosures indicate placeholder actions referring to steps from the documentation about how to make a codec at `docs/pages/howto.md`.

## Output Format (IMPORTANT)

When asked to add a codec, Copilot should:
1. Briefly justify the encoding (1–2 lines)
2. Provide full implementation (according to section _Adding a new codec to `codext`_ of the documentation at `docs/pages/howto.md`)
3. Provide tests (according to section _Self-generated tests_)
4. Add it to the `README.md` of the repository
5. Propose the update of the documentation (under the relevant page for the category of codec)

## Explicit Non-Goals

- No refactoring
- No performance optimization passes
- No linting-only changes
- No CI/CD changes
