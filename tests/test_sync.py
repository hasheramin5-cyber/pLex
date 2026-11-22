"""Tests for Continuous Bitstream Preamble Synchronizer & Deframer."""

import pytest
from pulselex.codec import encode_text
from pulselex.sync import deframe_pulses, sync_and_decode


def test_deframe_unsegmented_standard_stream():
    """Verify deframing a stream with zero whitespace."""
    original_text = "SOS"
    spaced_stream = encode_text(original_text, extended=False)
    # Strip all whitespace to simulate a contiguous bitstream
    continuous_stream = spaced_stream.replace(" ", "")

    decoded, meta = deframe_pulses(continuous_stream, extended=False)
    assert decoded == original_text
    assert meta["locked"] is True
    assert meta["start_offset"] == 0
    assert meta["blocks_decoded"] == len(original_text)


def test_deframe_with_leading_and_trailing_noise():
    """Verify lock acquisition when stream is preceded and followed by noise pulses."""
    original_text = "HELLO"
    continuous_stream = encode_text(original_text, extended=False).replace(" ", "")
    # Add random leading and trailing pulses
    leading_noise = ".-..-.-."  # 8 noise pulses
    trailing_noise = "-.-.-.-.-."
    noisy_stream = leading_noise + continuous_stream + trailing_noise

    decoded, meta = deframe_pulses(noisy_stream, extended=False)
    assert decoded == original_text
    assert meta["start_offset"] == len(leading_noise)
    assert meta["end_offset"] == len(leading_noise) + len(continuous_stream)


def test_deframe_with_single_bit_flip_in_start_marker():
    """Verify that deframer locks onto START marker even if 1 bit in START flipped."""
    original_text = "BEACON"
    continuous = list(encode_text(original_text, extended=False).replace(" ", ""))
    # Invert the 3rd bit of the 9-pulse START block
    continuous[2] = "." if continuous[2] == "-" else "-"
    corrupted_stream = "".join(continuous)

    decoded, meta = deframe_pulses(corrupted_stream, extended=False, max_start_distance=1)
    assert decoded == original_text
    assert meta["locked"] is True


def test_deframe_extended_secded_stream():
    """Verify continuous deframing in 10-bit SECDED mode."""
    original_text = "AIR GAP MSG"
    continuous = encode_text(original_text, extended=True).replace(" ", "")
    decoded, meta = deframe_pulses(continuous, extended=True)
    assert decoded == original_text
    assert meta["extended"] is True


def test_sync_and_decode_auto_detect():
    """Verify high-level sync_and_decode auto-detection."""
    text_9bit = "ALPHA"
    stream_9 = encode_text(text_9bit, extended=False).replace(" ", "")
    assert sync_and_decode("..noise.." + stream_9) == text_9bit

    text_10bit = "BRAVO"
    stream_10 = encode_text(text_10bit, extended=True).replace(" ", "")
    assert sync_and_decode("--noise--" + stream_10) == text_10bit


def test_deframe_fails_when_no_start_present():
    """Verify ValueError is raised if no START marker can be correlated."""
    noise_stream = ".-" * 20
    with pytest.raises(ValueError, match="no START preamble found"):
        deframe_pulses(noise_stream, extended=False)
