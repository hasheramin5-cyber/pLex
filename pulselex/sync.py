"""Continuous bitstream preamble synchronizer and sliding-window deframer for PulseLex."""

from __future__ import annotations

from .codec import (
    START,
    END,
    VALUE_TO_SYMBOL,
    encode_block,
    decode_block,
    bits_to_pulses,
    pulses_to_bits,
    DoubleErrorDetected,
)


def hamming_distance_str(s1: str, s2: str) -> int:
    if len(s1) != len(s2):
        raise ValueError("strings must be of equal length to compute Hamming distance")
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))


def deframe_pulses(
    raw_stream: str,
    extended: bool = False,
    max_start_distance: int = 1,
    strict: bool = True,
) -> tuple[str, dict]:
    """Synchronize onto continuous raw pulses, extract framed blocks, and decode text.

    Scans an unsegmented or noisy stream containing '.' and '-' characters by sliding
    a window of block_size (9 for standard, 10 for extended SECDED) to correlate with
    the known START marker codeword. Once locked, it steps block-by-block, correcting
    single-bit errors until reaching the END marker.

    Returns:
        tuple[str, dict]: Decoded text message and synchronization metadata.
    """
    # Strip any whitespace, punctuation, or non-pulse characters
    pulses = "".join(char for char in raw_stream if char in ".-")
    block_size = 10 if extended else 9

    if len(pulses) < block_size * 2:  # Must have at least START and END blocks
        raise ValueError(f"stream pulse count ({len(pulses)}) too short for framing")

    start_codeword = bits_to_pulses(encode_block(START, extended=extended))
    end_codeword = bits_to_pulses(encode_block(END, extended=extended))

    # Phase 1: Search for START marker with sliding window correlation
    lock_offset = None
    min_observed_distance = block_size + 1

    for offset in range(len(pulses) - block_size + 1):
        window = pulses[offset : offset + block_size]
        dist = hamming_distance_str(window, start_codeword)
        if dist < min_observed_distance:
            min_observed_distance = dist
        if dist <= max_start_distance:
            lock_offset = offset
            break

    if lock_offset is None:
        raise ValueError(
            f"frame synchronization failed: no START preamble found within Hamming distance {max_start_distance} "
            f"(min observed distance: {min_observed_distance})"
        )

    # Phase 2: Frame-locked block extraction and decoding
    decoded_symbols = []
    corrections = []
    double_errors = []
    pos = lock_offset + block_size
    end_offset = None

    while pos + block_size <= len(pulses):
        block_pulses = pulses[pos : pos + block_size]
        bits = pulses_to_bits(block_pulses)

        # Check if this block matches the END marker
        if hamming_distance_str(block_pulses, end_codeword) <= 1:
            end_offset = pos + block_size
            break

        try:
            value, corrected_idx = decode_block(bits, extended=extended)
            if corrected_idx is not None:
                corrections.append({"block_index": len(decoded_symbols), "bit_index": corrected_idx})

            if value == END:
                end_offset = pos + block_size
                break

            if value in VALUE_TO_SYMBOL:
                decoded_symbols.append(VALUE_TO_SYMBOL[value])
            else:
                if strict:
                    raise ValueError(f"reserved or unmapped symbol value {value} at offset {pos}")
                decoded_symbols.append("?")
        except DoubleErrorDetected as err:
            double_errors.append({"block_index": len(decoded_symbols), "offset": pos, "error": str(err)})
            if strict:
                raise
            decoded_symbols.append("?")

        pos += block_size

    if end_offset is None:
        if strict:
            raise ValueError("synchronization lost or message truncated: END marker not detected")
        end_offset = pos

    metadata = {
        "locked": True,
        "start_offset": lock_offset,
        "end_offset": end_offset,
        "total_pulses_consumed": end_offset - lock_offset,
        "blocks_decoded": len(decoded_symbols),
        "corrections": corrections,
        "double_errors": double_errors,
        "extended": extended,
    }

    return "".join(decoded_symbols), metadata


def sync_and_decode(stream: str, extended: bool | None = None, strict: bool = True) -> str:
    """High-level convenience function to synchronize and decode any pulse stream.

    If extended is None, tries standard 9-bit mode first; if synchronization fails,
    tries extended 10-bit SECDED mode.
    """
    if extended is not None:
        text, _ = deframe_pulses(stream, extended=extended, strict=strict)
        return text

    # Auto-detect mode by trying standard 9-bit first, then 10-bit extended
    try:
        text, _ = deframe_pulses(stream, extended=False, strict=strict)
        return text
    except ValueError:
        text, _ = deframe_pulses(stream, extended=True, strict=strict)
        return text
