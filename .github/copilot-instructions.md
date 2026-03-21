# Copilot Instructions — Enhancements Only

## Scope
This repository focuses on **adding new encoding/decoding schemes only**.

Copilot MUST:
- Propose **new codecs only**
- Avoid refactoring unrelated code
- Avoid dependency changes unless strictly required for the codec
- Avoid stylistic or formatting changes

## Context
This project extends Python's codecs with many encoding/decoding schemes and CLI tools.
It already includes a wide variety of bases, ciphers, compression, and niche encodings.

## Enhancement Guidelines

When adding a new encoding:
1. Check if it already exists in the project
2. Follow the existing codec structure and naming conventions
3. Provide:
   - `encode()` implementation
   - `decode()` implementation
   - Registration into the codec registry
4. Ensure CLI compatibility (if applicable)

## Implementation Constraints

- Pure Python preferred
- No heavy dependencies
- Deterministic transformations only
- Reversible encoding required unless explicitly documented

## Testing

Every new codec MUST include:
- Unit tests (encode/decode roundtrip)
- Edge cases (empty input, binary data if applicable)

## Documentation

Each codec must include:
- Short description
- Reference (standard, RFC, or algorithm source)
- Example usage

## Output Format (IMPORTANT)

When asked to add a codec, Copilot should:
1. Briefly justify the encoding (1–2 lines)
2. Provide full implementation
3. Provide tests
4. Provide documentation snippet

## Explicit Non-Goals

- No refactoring
- No performance optimization passes
- No linting-only changes
- No CI/CD changes