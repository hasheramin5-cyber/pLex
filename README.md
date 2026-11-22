# PulseLex

A Morse-inspired fixed-length alphabet with systematic Hamming (9,5) and Extended SECDED (10,5) forward error correction.

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](pyproject.toml)
[![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue.svg)](pyproject.toml)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-51%20passed-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen.svg)](tests/)

PulseLex is an experimental telecommunications and coding-theory research prototype. It investigates replacing the variable-length, timing-dependent characters of International Morse code with uniform five-bit payloads, rendering binary states as dot and dash pulses, and applying linear block codes to guarantee single-bit error correction and double-bit error detection.

It is an educational and micro-telemetry research artifact, not a replacement for operational high-bandwidth RF signaling and not a cryptographic cipher.

---

## Overview

Traditional International Morse code (ITU-R Recommendation M.1677-1) optimizes for human manual keying over clear channels. However, it relies heavily on temporal precision (1-unit element gaps, 3-unit character gaps, 7-unit word gaps) and provides no native forward error correction. Timing jitter or channel noise can cause framing loss across entire words.

PulseLex explores an alternative design:
- Every character occupies an invariant nine-pulse (or ten-pulse SECDED) block.
- Character framing is deterministic once stream synchronization is established.
- Isolated single-bit flips introduced during transmission are mathematically detected and corrected.
- The protocol provides an Extended Hamming (10,5) SECDED mode that detects double-bit errors to eliminate miscorrections.
- Built-in continuous bitstream sliding-window synchronization recovers frame lock over unsegmented pulse streams.
- Zero-dependency acoustic CW audio synthesis generates clean, raised-cosine shaped WAV tone bursts for over-the-air speaker-to-microphone air-gap transmission.

---

## Key Features

- **Shortened Hamming (9,5) & SECDED (10,5) Codec:** Systematic block code using four parity bits to protect five data bits ($d_{\min} = 3$), with an optional 10th overall parity bit providing Single Error Correction and Double Error Detection (SECDED, $d_{\min} = 4$).
- **Continuous Bitstream Preamble Synchronizer:** Sliding-window correlator locks onto raw, unsegmented pulse streams without relying on artificial whitespace separation.
- **Acoustic CW Waveform Synthesizer:** Standard-library audio keyer exports 16-bit mono PCM WAV files with smooth Hann-windowed rise/fall envelopes to prevent spectral splatter and key clicks.
- **32-Symbol Alphabet:** Comprehensive mapping of 26 uppercase English letters, space, three punctuation marks, and dedicated start/end framing markers.
- **Defensive Syndrome Decoding:** Distinguishes between zero errors, single-bit errors, and uncorrectable double-bit errors, raising `DoubleErrorDetected` rather than corrupting uncorrupted bits.
- **Binary Symmetric Channel Simulator:** Configurable Bernoulli bit-flip channel model for stochastic transmission experiments.
- **Reproducible Monte Carlo Benchmarks:** Automated simulation harness reporting empirical symbol error rates against uncoded baselines to CSV.
- **Academic Manuscript:** Complete LaTeX research paper (`paper/pulselex_paper.tex`) with formal derivations, TikZ diagrams, and BibTeX citations.
- **Zero External Dependencies:** Built entirely with the Python Standard Library.

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

Codewords use systematic 1-based indexing from 1 to 9 (or 10 in SECDED mode). Parity bits are assigned to powers of two (positions 1, 2, 4, 8), and five payload bits occupy the remaining positions (3, 5, 6, 7, 9):

```text
Standard (9,5):
Codeword Index:   1    2    3    4    5    6    7    8    9
Content Type:    p1   p2   d1   p4   d2   d3   d4   p8   d5
Bit Allocation: [ Parity ] [Data] [Parity] [   Data   ] [Parity] [Data]

Extended SECDED (10,5):
Codeword Index:   1    2    3    4    5    6    7    8    9   10
Content Type:    p1   p2   d1   p4   d2   d3   d4   p8   d5  p0 (Overall)
```

Under even parity, the check equations are:

$$\begin{aligned}
p_1 &= d_1 \oplus d_2 \oplus d_4 \oplus d_5 \\
p_2 &= d_1 \oplus d_3 \oplus d_4 \\
p_4 &= d_2 \oplus d_3 \oplus d_4 \\
p_8 &= d_5 \\
p_0 &= \bigoplus_{i=1}^9 c_i \quad \text{(SECDED mode only)}
\end{aligned}$$

### End-to-End Workflow

```mermaid
flowchart LR
    A[Text Input] --> B[Normalize & Frame]
    B --> C[5-Bit Payloads]
    C --> D[Hamming 9,5 / 10,5 SECDED]
    D --> E[Pulse Stream .-.-]
    E --> F[Continuous Synchronizer / Audio WAV]
    F --> G[Channel Noise / Air Gap]
    G --> H[Syndrome & Parity Validator]
    H --> I[Single-Bit Corrector / Double Error Guard]
    I --> J[Recovered Text]
```

---

## Mathematical Foundations

- **Code Rate ($R$):**
  $$R_{(9,5)} = \frac{5}{9} \approx 0.556, \quad R_{(10,5)} = \frac{5}{10} = 0.500$$
- **Redundancy Overhead:**
  $$\text{Overhead}_{(9,5)} = \frac{9 - 5}{5} \times 100\% = 80\%, \quad \text{Overhead}_{(10,5)} = 100\%$$
- **Minimum Hamming Distance & Error Bounds:**
  - Standard $(9,5)$: $d_{\min} = 3 \implies t = 1$ bit correction.
  - Extended $(10,5)$: $d_{\min} = 4 \implies t = 1$ bit correction, $2$ bits uncorrectable double-error detection (SECDED).
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

### 1. Command-Line Interface

#### Standard & SECDED Encoding
```bash
# Standard 9-bit encoding
pulselex encode "HELLO, WORLD?"

# Extended 10-bit SECDED encoding (Double-Error Detection)
pulselex encode --extended "HELLO, WORLD?"
```

#### Decoding Space-Separated Blocks
```bash
pulselex decode "-------.. .....---- .-.-.-... --..-.--- --..-.--- ...----.. ..-.--... -.-.-.-.. .--..--.. ...----.. .--....-- --..-.--- .-.-..--- -.-.--.-- .--------"
```

#### Continuous Stream Synchronization & Deframing
Recover messages from unsegmented, noisy bitstreams with leading/trailing noise:
```bash
pulselex sync-decode "..noise..-------..-..-..-..-....-.--------...noise.." --verbose
```

#### Acoustic CW Audio Synthesis (WAV Export)
Generate smooth, Hann-shaped 750 Hz audio tones:
```bash
pulselex audio "EMERGENCY" -o results/beacon.wav --freq 750 --dot-duration 0.050
```

### 2. Python API Example

```python
from pulselex import encode_text, decode_pulses, sync_and_decode, text_to_wav

# 1. Standard encoding & decoding
stream = encode_text("PULSELEX")
recovered = decode_pulses(stream)

# 2. Extended SECDED mode with 2-bit error detection
secded_stream = encode_text("AIR GAP MSG", extended=True)
recovered_secded = decode_pulses(secded_stream)

# 3. Synchronize continuous bitstream with arbitrary noise
raw_bitstream = "...noise..." + secded_stream.replace(" ", "") + "---noise---"
text = sync_and_decode(raw_bitstream, extended=True)
print("Deframed:", text)

# 4. Synthesize acoustic CW audio WAV file
wav_path = text_to_wav("SOS", "sos_beacon.wav", frequency_hz=800.0)
print(f"Audio exported to {wav_path}")
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
pytest
```

The 51 unit tests (98% line coverage) cover:
- Exhaustive single-bit error correction across all 32 valid payloads and all 9 bit positions (288 test cases).
- SECDED single-bit error correction (320 test cases) and exhaustive double-bit error detection (1,440 test cases).
- Continuous stream synchronization, preamble sliding-window correlation, and noise-boundary deframing.
- Audio sample synthesis, Hann envelope shaping, and standard 16-bit PCM WAV file header validation.
- Command-line interface subcommands (`encode`, `decode`, `sync-decode`, `audio`) and exit code handling.
- Monte Carlo experiment benchmarking runner and CSV dataset export.
- Edge cases, parameter boundary checking, and channel noiseless/full-noise states.

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
├── .github/
│   └── workflows/
│       └── ci.yml                   # Multi-OS, multi-version GitHub Actions CI
├── docs/
│   ├── MATHEMATICAL_QUESTIONS.txt   # Analytical coding theory exercises
│   ├── PulseLex_Technical_Report.md # Full architectural report (Markdown)
│   ├── PulseLex_Technical_Report.pdf# Full architectural report (PDF)
│   └── RESEARCH_BRIEF.txt           # High-level specification & hypotheses
├── paper/
│   └── pulselex_paper.tex           # LaTeX research paper
├── pulselex/
│   ├── __init__.py                  # Public exports
│   ├── audio.py                     # Acoustic CW WAV synthesizer
│   ├── channel.py                   # Binary symmetric channel model
│   ├── cli.py                       # Command-line interface
│   ├── codec.py                     # Alphabet mappings & (9,5)/(10,5) codec
│   ├── experiment.py                # Monte Carlo benchmark runner
│   └── sync.py                      # Continuous bitstream deframer & synchronizer
├── results/
│   ├── bit_error_experiment.csv     # 50,000-trial benchmark results
│   ├── experiment_summary.txt       # Benchmark summary
│   └── test_run.txt                 # Recorded test execution log
├── tests/
│   ├── test_audio.py                # Audio waveform unit tests
│   ├── test_channel.py              # Channel unit tests
│   ├── test_cli.py                  # CLI command unit tests
│   ├── test_codec.py                # Codec unit tests
│   ├── test_experiment.py           # Experiment runner unit tests
│   ├── test_secded.py               # SECDED 10-bit unit tests
│   └── test_sync.py                 # Synchronization & deframing tests
├── CONTRIBUTING.md                  # Development & contribution guidelines
├── LICENSE                          # MIT License
├── pyproject.toml                   # Project metadata & build configuration
├── references.bib                   # BibTeX bibliographic records
└── SECURITY.md                     # Security policy & reporting guidelines
```

---

## Limitations & Scope

- **Channel Realism:** The channel simulator implements an independent memoryless Binary Symmetric Channel.
- **Alphabet Boundary:** The alphabet is restricted to 32 states (uppercase English, space, period, comma, question mark, start, end). Digits and lowercase letters are normalized or rejected.
- **Acoustic Detection:** The audio module currently synthesizes acoustic waveforms; software-defined microphone tone demodulation is planned for subsequent phases.

---

## Contributing

Contributions, bug reports, and research extensions are welcome:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/extension-name`).
3. Ensure all tests pass (`pytest`).
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
