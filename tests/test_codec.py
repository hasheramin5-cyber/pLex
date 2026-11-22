import pytest
from pulselex.codec import (
    encode_block,
    decode_block,
    encode_text,
    decode_pulses,
    int_to_bits,
    pulses_to_bits,
    START,
    END,
)


def test_all_32_payloads_round_trip():
    for value in range(32):
        decoded, corrected = decode_block(encode_block(value))
        assert decoded == value
        assert corrected is None


def test_corrects_every_single_bit_error():
    for value in range(32):
        original = encode_block(value)
        for position in range(9):
            damaged = original.copy()
            damaged[position] ^= 1
            decoded, corrected = decode_block(damaged)
            assert decoded == value
            assert corrected == position


def test_text_round_trip():
    message = "HELLO, WORLD?"
    assert decode_pulses(encode_text(message)) == message


def test_lowercase_is_normalized():
    assert decode_pulses(encode_text("pulselex")) == "PULSELEX"


def test_unsupported_character_is_rejected():
    with pytest.raises(ValueError):
        encode_text("HELLO!")


def test_int_to_bits_out_of_range():
    with pytest.raises(ValueError, match="fit in 5 bits"):
        int_to_bits(32, 5)
    with pytest.raises(ValueError, match="fit in 5 bits"):
        int_to_bits(-1, 5)


def test_decode_block_invalid_input():
    with pytest.raises(ValueError, match="must contain exactly"):
        decode_block([0, 1, 0])
    with pytest.raises(ValueError, match="must contain exactly"):
        decode_block([0, 1, 0, 1, 0, 1, 0, 1, 2])


def test_pulses_to_bits_invalid_char():
    with pytest.raises(ValueError, match="may contain only"):
        pulses_to_bits("..x..----")


def test_decode_pulses_empty_stream():
    assert decode_pulses("") == ""


def test_decode_pulses_missing_markers():
    stream = encode_text("TEST", include_markers=False)
    with pytest.raises(ValueError, match="missing start or end marker"):
        decode_pulses(stream, expect_markers=True)


def test_decode_pulses_reserved_symbol_in_body():
    # Construct a stream where payload is START (30) inside the text
    blocks = [encode_block(START), encode_block(START), encode_block(END)]
    stream = " ".join("".join("-" if b else "." for b in blk) for blk in blocks)
    with pytest.raises(ValueError, match="reserved or unexpected symbol"):
        decode_pulses(stream)
