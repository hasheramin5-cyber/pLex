"""Reproducible Monte Carlo experiment for uncoded vs Hamming-coded symbols."""

from __future__ import annotations
import argparse
import csv
import random
from pathlib import Path

from .codec import encode_block, decode_block
from .channel import transmit


def run_experiment(trials: int = 20000, seed: int = 7) -> list[dict]:
    rng = random.Random(seed)
    probabilities = [0.001, 0.005, 0.01, 0.02, 0.05, 0.10]
    rows = []

    for p in probabilities:
        raw_errors = corrected_errors = corrected_blocks = 0
        for _ in range(trials):
            value = rng.randrange(32)
            payload = [(value >> shift) & 1 for shift in range(4, -1, -1)]
            raw_received = transmit(payload, p, rng)
            raw_decoded = 0
            for bit in raw_received:
                raw_decoded = (raw_decoded << 1) | bit
            raw_errors += raw_decoded != value

            codeword = encode_block(value)
            noisy = transmit(codeword, p, rng)
            decoded, corrected_index = decode_block(noisy)
            corrected_blocks += corrected_index is not None
            corrected_errors += decoded != value

        rows.append({
            "bit_error_probability": p,
            "trials": trials,
            "uncoded_symbol_error_rate": raw_errors / trials,
            "hamming_9_5_symbol_error_rate": corrected_errors / trials,
            "blocks_with_correction": corrected_blocks,
            "uncoded_bits_per_symbol": 5,
            "coded_bits_per_symbol": 9,
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--output", default="results/bit_error_experiment.csv")
    args = parser.parse_args()

    rows = run_experiment(args.trials, args.seed)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
