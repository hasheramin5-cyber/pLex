import random
import pytest
from pulselex.channel import transmit, hamming_distance


def test_zero_noise_preserves_bits():
    bits = [0, 1, 1, 0, 1]
    assert transmit(bits, 0.0, random.Random(3)) == bits


def test_full_noise_flips_all_bits():
    bits = [0, 1, 1, 0, 1]
    assert transmit(bits, 1.0, random.Random(3)) == [1, 0, 0, 1, 0]


def test_hamming_distance():
    assert hamming_distance([0, 1, 1], [1, 1, 0]) == 2


def test_hamming_distance_unequal_length():
    with pytest.raises(ValueError, match="must have equal length"):
        hamming_distance([0, 1], [1, 1, 0])


def test_invalid_probability():
    with pytest.raises(ValueError):
        transmit([0, 1], 1.2)
    with pytest.raises(ValueError):
        transmit([0, 1], -0.1)
