"""PulseLex symbol mapping and Hamming (9,5) block codec."""

from __future__ import annotations

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
SYMBOL_TO_VALUE = {char: index for index, char in enumerate(ALPHABET)}
SYMBOL_TO_VALUE.update({" ": 26, ".": 27, ",": 28, "?": 29})
VALUE_TO_SYMBOL = {value: symbol for symbol, value in SYMBOL_TO_VALUE.items()}
START = 30
END = 31

# Payload positions are 3, 5, 6, 7, 9 (one-indexed).
DATA_POSITIONS = (2, 4, 5, 6, 8)
PARITY_POSITIONS = (0, 1, 3, 7)


def int_to_bits(value: int, width: int = 5) -> list[int]:
    if not 0 <= value < (1 << width):
        raise ValueError(f"value must fit in {width} bits")
    return [(value >> shift) & 1 for shift in range(width - 1, -1, -1)]


def bits_to_int(bits: list[int]) -> int:
    value = 0
    for bit in bits:
        value = (value << 1) | bit
    return value


def encode_block(value: int) -> list[int]:
    """Encode one 5-bit value as a 9-bit Hamming (9,5) codeword."""
    data = int_to_bits(value, 5)
    code = [0] * 9
    for position, bit in zip(DATA_POSITIONS, data):
        code[position] = bit

    # Even parity: each parity check covers positions whose index has that bit set.
    for parity_position in PARITY_POSITIONS:
        parity_mask = parity_position + 1
        parity = 0
        for index in range(9):
            if (index + 1) & parity_mask and index != parity_position:
                parity ^= code[index]
        code[parity_position] = parity
    return code


def decode_block(received: list[int]) -> tuple[int, int | None]:
    """Decode a 9-bit block; return (payload, corrected_zero_based_bit_index)."""
    if len(received) != 9 or any(bit not in (0, 1) for bit in received):
        raise ValueError("a block must contain exactly nine binary bits")

    code = received.copy()
    syndrome = 0
    for parity_position in PARITY_POSITIONS:
        parity_mask = parity_position + 1
        check = 0
        for index in range(9):
            if (index + 1) & parity_mask:
                check ^= code[index]
        if check:
            syndrome |= parity_mask

    corrected = None
    if 1 <= syndrome <= 9:
        corrected = syndrome - 1
        code[corrected] ^= 1
    # A syndrome above 9 can arise from multiple errors in this shortened
    # code. Such a pattern is outside the guaranteed correction region;
    # leave it untouched rather than pretending it is a correctable bit.

    payload = [code[position] for position in DATA_POSITIONS]
    return bits_to_int(payload), corrected


def bits_to_pulses(bits: list[int]) -> str:
    return "".join("-" if bit else "." for bit in bits)


def pulses_to_bits(pulses: str) -> list[int]:
    if any(symbol not in ".-" for symbol in pulses):
        raise ValueError("pulse blocks may contain only '.' and '-'")
    return [1 if symbol == "-" else 0 for symbol in pulses]


def encode_text(text: str, include_markers: bool = True) -> str:
    """Encode supported text to space-separated nine-pulse blocks."""
    normalized = text.upper()
    unsupported = sorted(set(normalized) - set(SYMBOL_TO_VALUE))
    if unsupported:
        raise ValueError(f"unsupported characters: {unsupported}")

    values = ([START] if include_markers else [])
    values.extend(SYMBOL_TO_VALUE[char] for char in normalized)
    if include_markers:
        values.append(END)
    return " ".join(bits_to_pulses(encode_block(value)) for value in values)


def decode_pulses(stream: str, expect_markers: bool = True) -> str:
    """Decode a space-separated stream of nine-pulse blocks."""
    blocks = stream.split()
    if not blocks:
        return ""

    values = []
    for block in blocks:
        bits = pulses_to_bits(block)
        value, _ = decode_block(bits)
        values.append(value)

    if expect_markers:
        if values[0] != START or values[-1] != END:
            raise ValueError("missing start or end marker")
        values = values[1:-1]

    output = []
    for value in values:
        if value not in VALUE_TO_SYMBOL:
            raise ValueError(f"reserved or unexpected symbol value: {value}")
        output.append(VALUE_TO_SYMBOL[value])
    return "".join(output)
