# Contributing to PulseLex

Contributions, bug reports, and research extensions are welcome. PulseLex is an academic and educational research prototype designed to explore linear block error-correction codes in discrete telegraphic signaling.

## Development Setup

1. Clone the repository and checkout a feature branch:
   ```bash
   git clone https://github.com/hasheramin5-cyber/pLex.git
   cd pLex
   git checkout -b feature/your-feature-name
   ```

2. Create a virtual environment with Python 3.10 or newer:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install in editable development mode with testing dependencies:
   ```bash
   python -m pip install -e ".[dev]" pytest-cov
   ```

## Running Tests

Run the complete test suite and verify code coverage:
```bash
pytest -v --cov=pulselex
```

Ensure all tests pass and that any new functionality is accompanied by comprehensive unit tests.

## Coding Guidelines

- Adhere to PEP 8 styling conventions.
- Maintain pure functions with type annotations (`from __future__ import annotations`).
- Maintain zero runtime dependencies for the core package (use only Python Standard Library).
- Ensure backward compatibility with existing 9-bit and 10-bit block formats.

## Submitting Pull Requests

1. Commit your changes with descriptive, conventional commit messages (`feat: ...`, `fix: ...`, `docs: ...`, `test: ...`).
2. Push your feature branch to your fork.
3. Open a Pull Request against `main`.
4. Ensure continuous integration tests pass on GitHub Actions.
