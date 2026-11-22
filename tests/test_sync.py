"""Tests for Continuous Bitstream Preamble Synchronizer & Deframer."""

import pytest
from pulselex.codec import encode_text, encode_block, START, END, DoubleErrorDetected
from pulselex.sync import deframe_pulses, sync_and_decode, hamming_distance_str


def test_hamming_distance_str_unequal():
    with pytest.raises(ValueError, match="equal length"):
        hamming_distance_str("...", "..")


def test_deframe_unsegmented_standard_stream():
    """Verify deframing a stream with zero whitespace."""
    original_text = "SOS"
    spaced_stream = encode_text(original_text, extended=False)
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
    leading_noise = ".-..-.-."
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


def test_deframe_stream_too_short():
    with pytest.raises(ValueError, match="too short"):
        deframe_pulses("...", extended=False)


def test_deframe_missing_end_marker_strict_vs_lenient():
    # Stream without END marker
    start = "".join("-" if b else "." for b in encode_block(START))
    char = "".join("-" if b else "." for b in encode_block(0))  # 'A'
    stream = start + char
    with pytest.raises(ValueError, match="END marker not detected"):
        deframe_pulses(stream, extended=False, strict=True)

    decoded, meta = deframe_pulses(stream, extended=False, strict=False)
    assert decoded == "A"


def test_deframe_unmapped_symbol_strict_vs_lenient():
    start = "".join("-" if b else "." for b in encode_block(START))
    end = "".join("-" if b else "." for b in encode_block(END))
    # Reserved value 30 inside payload
    body = "".join("-" if b else "." for b in encode_block(START))
    stream = start + body + end

    with pytest.raises(ValueError, match="reserved or unmapped"):
        deframe_pulses(stream, extended=False, strict=True)

    decoded, meta = deframe_pulses(stream, extended=False, strict=False)
    assert decoded == "?"


def test_deframe_double_error_strict_vs_lenient():
    start = "".join("-" if b else "." for b in encode_block(START, extended=True))
    end = "".join("-" if b else "." for b in encode_block(END, extended=True))
    # Block with 2 bit flips
    blk = encode_block(0, extended=True)
    blk[0] ^= 1
    blk[1] ^= 1
    corrupted_body = "".join("-" if b else "." for b in blk)
    stream = start + corrupted_body + end

    with pytest.raises(DoubleErrorDetected):
        deframe_pulses(stream, extended=True, strict=True)

    decoded, meta = deframe_pulses(stream, extended=True, strict=False)
    assert decoded == "?"
    assert len(meta["double_errors"]) == 1
