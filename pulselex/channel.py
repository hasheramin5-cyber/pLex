"""Simple independent bit-flip channel."""

from __future__ import annotations
import random


def transmit(bits: list[int], bit_error_probability: float, rng: random.Random | None = None) -> list[int]:
    if not 0.0 <= bit_error_probability <= 1.0:
        raise ValueError("bit_error_probability must be between 0 and 1")
    rng = rng or random.Random()
    return [bit ^ int(rng.random() < bit_error_probability) for bit in bits]


def hamming_distance(left: list[int], right: list[int]) -> int:
    if len(left) != len(right):
        raise ValueError("bit sequences must have equal length")
    return sum(a != b for a, b in zip(left, right))
