"""Tests for Extended Hamming (10,5) SECDED codec."""

import pytest
from pulselex.codec import (
    encode_block,
    decode_block,
    encode_text,
    decode_pulses,
    DoubleErrorDetected,
)


def test_secded_all_32_payloads_round_trip():
    """Verify that all 32 values encode to 10-bit codewords and decode cleanly."""
    for value in range(32):
        codeword = encode_block(value, extended=True)
        assert len(codeword) == 10
        # Overall parity must be even
        assert sum(codeword) % 2 == 0

        decoded, corrected = decode_block(codeword, extended=True)
        assert decoded == value
        assert corrected is None


def test_secded_corrects_every_single_bit_error():
    """Verify that every single-bit error across all 10 bit positions is corrected (320 cases)."""
    for value in range(32):
        original = encode_block(value, extended=True)
        for position in range(10):
            damaged = original.copy()
            damaged[position] ^= 1

            decoded, corrected = decode_block(damaged, extended=True)
            assert decoded == value
            assert corrected == position


def test_secded_detects_every_double_bit_error():
    """Verify that every 2-bit error combination raises DoubleErrorDetected (1,440 cases)."""
    for value in range(32):
        original = encode_block(value, extended=True)
        # Check all C(10, 2) = 45 pairs of bit flips
        for pos1 in range(10):
            for pos2 in range(pos1 + 1, 10):
                damaged = original.copy()
                damaged[pos1] ^= 1
                damaged[pos2] ^= 1

                with pytest.raises(DoubleErrorDetected):
                    decode_block(damaged, extended=True)


def test_secded_text_round_trip():
    message = "EMERGENCY, REPORT?"
    stream = encode_text(message, extended=True)
    blocks = stream.split()
    for block in blocks:
        assert len(block) == 10

    recovered = decode_pulses(stream, extended=True)
    assert recovered == message


def test_secded_auto_detects_10_bit_blocks():
    message = "SECDED TEST"
    stream = encode_text(message, extended=True)
    # decode_pulses should auto-detect extended=True from 10-character blocks
    assert decode_pulses(stream) == message
