import pytest
from pulselex.codec import encode_block, decode_block, encode_text, decode_pulses


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
