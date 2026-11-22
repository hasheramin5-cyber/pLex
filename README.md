# PulseLex

A Morse-inspired fixed-length alphabet with systematic Hamming (9,5) forward error correction.

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](pyproject.toml)
[![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue.svg)](pyproject.toml)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-9%20passed-brightgreen.svg)](tests/)

PulseLex is an experimental telecommunications and coding-theory research prototype. It investigates replacing the variable-length, timing-dependent characters of International Morse code with uniform five-bit payloads, rendering binary states as dot and dash pulses, and applying a shortened systematic Hamming (9,5) block code to correct single-bit errors within every nine-pulse character block.

It is an educational research artifact, not a replacement for operational Morse signaling and not a cryptographic cipher.

---

## Overview

Traditional International Morse code (ITU-R Recommendation M.1677-1) optimizes for human manual keying over clear channels. However, it relies heavily on temporal precision (1-unit element gaps, 3-unit character gaps, 7-unit word gaps) and provides no native forward error correction. Timing jitter or channel noise can cause framing loss across entire words.

PulseLex explores an alternative design:
- Every character occupies an invariant nine-pulse block.
- Character framing is deterministic once stream synchronization is established.
- Isolated single-bit flips introduced during transmission are mathematically detected and corrected.
- The protocol incurs an 80% redundancy overhead (9 transmitted pulses vs. 5 uncoded bits) in exchange for significant symbol error rate reduction under moderate noise.

---

## Key Features

- **Shortened Hamming (9,5) Codec:** Systematic block code using four parity bits to protect five data bits, guaranteeing single-bit error correction ($d_{\min} = 3$).
- **32-Symbol Alphabet:** Comprehensive mapping of 26 uppercase English letters, space, three punctuation marks, and dedicated start/end framing markers.
- **Defensive Syndrome Decoding:** Detects when error patterns fall outside the single-bit correction region (syndromes 10 through 15 in shortened space) to avoid erroneous bit alteration.
- **Binary Symmetric Channel Simulator:** Configurable Bernoulli bit-flip channel model for stochastic transmission experiments.
- **Reproducible Monte Carlo Benchmarks:** Automated simulation harness reporting empirical symbol error rates against uncoded baselines to CSV.
- **Academic Manuscript:** Complete LaTeX research paper (`paper/pulselex_paper.tex`) with formal derivations, TikZ diagrams, and BibTeX citations.
- **Zero Runtime Dependencies:** Built entirely with the Python Standard Library.

---

## Symbol Alphabet

Each symbol maps to a 5-bit binary payload ($2^5 = 32$ unique states):

| Decimal Value | 5-Bit Payload | Symbol | Description |
|---:|:---:|:---:|---|
| 0–25 | `00000`–`11001` | A–Z | Uppercase Latin alphabet |
| 26 | `11010` | Space | Word delimiter |
| 27 | `11011` | `.` | Full stop |
| 28 | `11100` | `,` | Comma |
| 29 | `11101` | `?` | Question mark |
| 30 | `11110` | `START` | Message preamble marker |
| 31 | `11111` | `END` | Message postamble marker |

A binary `0` is rendered as a dot (`.`), and a binary `1` is rendered as a dash (`-`).

---

## Technical Architecture

Codewords use systematic 1-based indexing from 1 to 9. Parity bits are assigned to powers of two (positions 1, 2, 4, 8), and five payload bits occupy the remaining positions (3, 5, 6, 7, 9):

```text
Codeword Index:   1    2    3    4    5    6    7    8    9
Content Type:    p1   p2   d1   p4   d2   d3   d4   p8   d5
Bit Allocation: [ Parity ] [Data] [Parity] [   Data   ] [Parity] [Data]
```

Under even parity, the four check equations are:

$$\begin{aligned}
p_1 &= d_1 \oplus d_2 \oplus d_4 \oplus d_5 \\
p_2 &= d_1 \oplus d_3 \oplus d_4 \\
p_4 &= d_2 \oplus d_3 \oplus d_4 \\
p_8 &= d_5
\end{aligned}$$

### End-to-End Workflow

```mermaid
flowchart LR
    A[Text Input] --> B[Normalize & Frame]
    B --> C[5-Bit Payloads]
    C --> D[Hamming 9,5 Encoder]
    D --> E[Pulse Stream .-.-]
    E --> F[Channel Noise BSC]
    F --> G[Syndrome Calculator]
    G --> H[Single-Bit Corrector]
    H --> I[Strip Markers]
    I --> J[Recovered Text]
```

---

## Mathematical Foundations

- **Code Rate ($R$):**
  $$R = \frac{k}{n} = \frac{5}{9} \approx 0.556$$
- **Redundancy Overhead:**
  $$\frac{n - k}{k} \times 100\% = \frac{9 - 5}{5} \times 100\% = 80\%$$
- **Uncoded Symbol Error Rate (SER):** For independent bit-flip probability $p$:
  $$P_{\text{uncoded}} = 1 - (1 - p)^5$$
  At $p = 0.01$, $P_{\text{uncoded}} \approx 0.04901$ (4.90%).
- **Hamming Block Failure Rate ($P_{\ge 2}$):** Probability of two or more bit errors in a 9-bit block:
  $$P_{\ge 2} = 1 - (1 - p)^9 - 9p(1 - p)^8$$
  At $p = 0.01$, $P_{\ge 2} \approx 0.00344$ (0.34%), delivering a ~14.3x reduction in symbol error probability.

---

## Installation

### Prerequisites
- Python 3.10 or newer.

### Editable Development Install
```bash
git clone https://github.com/hasheramin5-cyber/pLex.git
cd pLex
python -m pip install -e .
```

### Development Dependencies
To install test utilities:
```bash
python -m pip install -e ".[dev]"
```

---

## Quick Start & Usage

### Command-Line Interface

#### Encode Text to Pulses
```bash
pulselex encode "HELLO, WORLD?"
```

Output:
```text
-------.. .....---- .-.-.-... --..-.--- --..-.--- ...----.. ..-.--... -.-.-.-.. .--..--.. ...----.. .--....-- --..-.--- .-.-..--- -.-.--.-- .--------
```
*(Block 1 is the START marker `-------..`; block 15 is the END marker `.--------`.)*

#### Decode Pulses to Text
```bash
pulselex decode "-------.. .....---- .-.-.-... --..-.--- --..-.--- ...----.. ..-.--... -.-.-.-.. .--..--.. ...----.. .--....-- --..-.--- .-.-..--- -.-.--.-- .--------"
```

Output:
```text
HELLO, WORLD?
```

#### Run Without Prior Installation
You can invoke the CLI module directly by setting `PYTHONPATH`:
```bash
# Linux / macOS
PYTHONPATH="." python -m pulselex.cli encode "HELLO"

# Windows PowerShell
$env:PYTHONPATH="."; python -m pulselex.cli encode "HELLO"
```

### Python API Example

```python
from pulselex import encode_text, decode_pulses

# Encode string into framed 9-pulse blocks
stream = encode_text("PULSELEX")
print(stream)

# Decode stream back to verified string
recovered = decode_pulses(stream)
print(recovered)
```

---

## Empirical Benchmarks

The project includes an empirical Monte Carlo benchmarking tool that evaluates symbol error rates across noise rates.

### Run Experiment
```bash
python -m pulselex.experiment --trials 50000 --seed 7 --output results/bit_error_experiment.csv
```

### Reference Results (50,000 trials per probability, seed 7)

| Bit Error Prob ($p$) | Uncoded 5-Bit SER | PulseLex (9,5) SER | Blocks Corrected | SER Reduction |
|---:|---:|---:|---:|---:|
| 0.001 | 0.004740 | 0.000000 | 421 | Complete (0 errors) |
| 0.005 | 0.024440 | 0.001000 | 2,183 | 24.4x |
| 0.010 | 0.048720 | 0.003260 | 4,329 | 14.9x |
| 0.020 | 0.095600 | 0.012260 | 8,303 | 7.8x |
| 0.050 | 0.229600 | 0.068120 | 17,175 | 3.4x |
| 0.100 | 0.409200 | 0.211820 | 26,360 | 1.9x |

*Reference data stored in `results/bit_error_experiment.csv` and summarized in `results/experiment_summary.txt`.*

---

## Testing

Run the automated test suite using pytest:

```bash
# If package is installed via pip:
pytest

# If running uninstalled from repository root:
python -m pytest -o pythonpath=.
```

The test suite covers:
- Exhaustive single-bit error correction across all 32 valid payloads and all 9 bit positions (288 test cases).
- Full round-trip encoding and decoding across supported symbols and sentences.
- Boundary conditions, probability validation, and channel noiseless/full-noise states.

---

## Compiling the Research Paper

The repository contains an academic manuscript (`paper/pulselex_paper.tex`) detailing the protocol's mathematical proofs and findings.

To compile using a standard LaTeX distribution:
```bash
pdflatex -output-directory=paper paper/pulselex_paper.tex
bibtex paper/pulselex_paper
pdflatex -output-directory=paper paper/pulselex_paper.tex
pdflatex -output-directory=paper paper/pulselex_paper.tex
```

---

## Repository Structure

```text
PulseLex/
├── docs/
│   ├── MATHEMATICAL_QUESTIONS.txt   # Analytical coding theory exercises
│   ├── PulseLex_Technical_Report.md # Full architectural report (Markdown)
│   ├── PulseLex_Technical_Report.pdf# Full architectural report (PDF)
│   └── RESEARCH_BRIEF.txt           # High-level specification & hypotheses
├── paper/
│   └── pulselex_paper.tex           # LaTeX research paper
├── pulselex/
│   ├── __init__.py                  # Public exports
│   ├── channel.py                   # Binary symmetric channel model
│   ├── cli.py                       # Command-line interface
│   ├── codec.py                     # Alphabet mappings & (9,5) codec
│   └── experiment.py                # Monte Carlo benchmark runner
├── results/
│   ├── bit_error_experiment.csv     # 50,000-trial benchmark results
│   ├── experiment_summary.txt       # Benchmark summary
│   └── test_run.txt                 # Recorded test execution log
├── tests/
│   ├── test_channel.py              # Channel unit tests
│   └── test_codec.py                # Codec unit tests
├── pyproject.toml                   # Project metadata & build configuration
├── references.bib                   # BibTeX bibliographic records
└── LICENSE                          # MIT License
```

---

## Limitations & Scope

- **Channel Realism:** The simulator implements an independent memoryless Binary Symmetric Channel. It does not model burst errors, multipath fading, or continuous pulse timing.
- **Framing Dependency:** The current decoder expects pre-segmented, whitespace-separated blocks. It does not implement sliding-window preamble detection for unsegmented bitstreams.
- **Two-Bit Errors:** As with all standard Hamming codes with minimum distance 3, two bit flips within a block produce an active syndrome pointing to an uncorrupted bit, causing miscorrection.
- **Alphabet Boundary:** The alphabet is restricted to 32 states (uppercase English, space, period, comma, question mark, start, end). Digits and lowercase letters are normalized or rejected.

---

## Contributing

Contributions, bug reports, and research extensions are welcome:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/extension-name`).
3. Ensure all tests pass (`python -m pytest -o pythonpath=.`).
4. Commit your changes with descriptive commit messages.
5. Open a Pull Request.

---

## References & Citation

If you reference or build upon PulseLex in academic work, please cite:

```bibtex
@misc{pulselex2026,
  author       = {{PulseLex Research Prototype}},
  title        = {PulseLex: A Morse-Inspired Fixed-Length Alphabet with Single-Bit Error Correction},
  year         = {2026},
  howpublished = {\url{https://github.com/hasheramin5-cyber/pLex}}
}
```

Primary foundational literature:
- International Telecommunication Union, *Recommendation ITU-R M.1677-1: International Morse Code*, 2009.
- R. W. Hamming, *Error Detecting and Error Correcting Codes*, Bell System Technical Journal, 1950.
- T. M. Cover and J. A. Thomas, *Elements of Information Theory*, Wiley, 2006.

---

## License

This project is licensed under the terms of the [MIT License](LICENSE).
