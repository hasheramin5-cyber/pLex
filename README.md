# PulseLex

**A Morse-inspired, fixed-length alphabet with single-bit error correction**

PulseLex is an experimental text-encoding protocol. It maps a compact alphabet to five-bit symbols, converts bits into dot/dash pulses, and applies a Hamming-style `(9,5)` code to correct one flipped bit per character block.

It is a research prototype, not a replacement for International Morse code and not a cryptographic system.

## Research question

Can a fixed-length, Hamming-coded Morse-inspired alphabet improve decoding reliability over uncoded fixed-width symbols and conventional Morse under a simulated binary-noise channel, and what transmission-length cost does that reliability introduce?

## What is included

- A working Python encoder and decoder.
- A `(9,5)` Hamming encoder/decoder with single-bit correction.
- A simple bit-flip channel simulator.
- Reproducible experiments and CSV results.
- A LaTeX research paper (`paper/pulselex_paper.tex`).
- A plain-text research brief and mathematical questions.
- Tests and a small command-line interface.

## Symbol design

Five payload bits represent 32 symbols:

| Value | Symbol |
|---:|---|
| 0–25 | A–Z |
| 26 | Space |
| 27 | `.` |
| 28 | `,` |
| 29 | `?` |
| 30 | Start marker |
| 31 | End marker |

A payload bit `0` is shown as a dot (`.`), and `1` as a dash (`-`). The payload is placed in positions 3, 5, 6, 7, and 9 of a nine-bit Hamming block. Positions 1, 2, 4, and 8 contain parity bits.

Every character therefore uses nine pulse units. The start and end markers are encoded as ordinary nine-pulse blocks. A receiver can use the fixed block length to segment the stream after synchronization.

## Quick start

Requires Python 3.10 or newer.

```bash
python -m pip install -e .
pulselex encode "HELLO, WORLD?"
pulselex decode "..."  # replace with a PulseLex pulse stream
python -m pytest
python -m pulselex.experiment --trials 20000 --seed 7
```

To compile the research paper from the repository root, use a LaTeX installation with `pdflatex` and BibTeX:

```bash
pdflatex -output-directory=paper paper/pulselex_paper.tex
bibtex paper/pulselex_paper
pdflatex -output-directory=paper paper/pulselex_paper.tex
pdflatex -output-directory=paper paper/pulselex_paper.tex
```

You can also run the CLI directly from the repository:

```bash
python -m pulselex.cli encode "HELLO"
python -m pulselex.cli decode "PULSE_STREAM_HERE"
```

The stream format uses spaces between nine-pulse blocks. Each block contains only `.` and `-`.

## Mathematical core

For payload bits \(d_1,\ldots,d_5\), placed at codeword positions 3, 5, 6, 7, and 9:

\[
\begin{aligned}
p_1 &= d_1 \oplus d_2 \oplus d_4 \oplus d_5,\\
p_2 &= d_1 \oplus d_3 \oplus d_4,\\
p_4 &= d_2 \oplus d_3 \oplus d_4,\\
p_8 &= d_5.
\end{aligned}
\]

The resulting `(9,5)` code has minimum Hamming distance 3. It can correct one bit error per block. It does not guarantee correction of two or more errors in the same block.

## Research integrity

The project distinguishes established foundations from the proposed experiment:

- International Morse code is standardized in ITU-R Recommendation M.1677-1.
- Hamming's classic work established error-detecting and error-correcting codes.
- PulseLex combines a five-bit symbol alphabet, pulse rendering, fixed-size framing, and a Hamming `(9,5)` block code as an experimental design.

The novelty claim is deliberately limited: PulseLex is a small educational prototype and evaluation, not a claim to have invented Morse coding or Hamming coding.

## Limitations

- The simulator models independent bit flips, not realistic radio fading, timing drift, burst noise, or synchronization loss.
- The decoder assumes nine-pulse block boundaries are already known.
- A two-bit error can be miscorrected by a standard Hamming decoder.
- The pulse representation uses equal abstract bit slots. It does not implement Morse timing ratios.
- The current alphabet is ASCII-oriented and does not support arbitrary Unicode text.

## Repository map

```text
PulseLex/
├── paper/
│   └── pulselex_paper.tex
├── pulselex/
│   ├── __init__.py
│   ├── codec.py
│   ├── channel.py
│   ├── cli.py
│   └── experiment.py
├── tests/
│   ├── test_codec.py
│   └── test_channel.py
├── docs/
│   ├── MATHEMATICAL_QUESTIONS.txt
│   └── RESEARCH_BRIEF.txt
├── results/
│   ├── experiment_summary.txt
│   └── bit_error_experiment.csv
├── references.bib
├── pyproject.toml
└── LICENSE
```

## License

MIT. See `LICENSE`.
