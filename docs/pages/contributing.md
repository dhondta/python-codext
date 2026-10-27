Contributions are welcome, especially **new codecs** and **new macros**.

### Reporting issues

Open an issue on [GitHub](https://github.com/dhondta/python-codext/issues) and include:

- the CodExt and Python versions;
- the codec name, the input and the exact command or code used;
- the expected and the actual output.

### Adding a codec or a macro

- **Codec**: follow [Create your codec](howto.md), add examples or tests, then open a [pull request](https://github.com/dhondta/python-codext/pulls).
- **Macro**: open a [pull request](https://github.com/dhondta/python-codext/pulls) with your updated version of [`macros.json`](https://github.com/dhondta/python-codext/blob/main/src/codext/macros.json).

### Development setup

```sh
git clone https://github.com/dhondta/python-codext
cd python-codext
pip install -e .
pip install pytest pytest-cov
pytest --cov=codext
```

CI (`.github/workflows/python-package.yml`) installs the package and runs the tests on Python 3.10 to 3.13.

### Security

Please do **not** report vulnerabilities in public issues. See the [security policy](https://github.com/dhondta/python-codext/blob/main/SECURITY.md): report them privately through the repository's *Security* tab (*Report a vulnerability*).

Dependencies are monitored by Dependabot and audited with [pip-audit](https://github.com/pypa/pip-audit) by the `security` workflow (`.github/workflows/security.yml`), on every push and pull request to `main` and weekly.
