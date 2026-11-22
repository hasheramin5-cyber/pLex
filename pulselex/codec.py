"""PulseLex symbol mapping and Hamming (9,5) / (10,5) SECDED block codec."""

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
OVERALL_PARITY_POSITION = 9  # Zero-indexed 10th bit in SECDED mode


class DoubleErrorDetected(ValueError):
    """Raised when an uncorrectable double-bit error is detected in SECDED mode."""


def int_to_bits(value: int, width: int = 5) -> list[int]:
    if not 0 <= value < (1 << width):
        raise ValueError(f"value must fit in {width} bits")
    return [(value >> shift) & 1 for shift in range(width - 1, -1, -1)]


def bits_to_int(bits: list[int]) -> int:
    value = 0
    for bit in bits:
        value = (value << 1) | bit
    return value


def encode_block(value: int, extended: bool = False) -> list[int]:
    """Encode one 5-bit value as a 9-bit Hamming (9,5) or 10-bit SECDED (10,5) codeword."""
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

    if extended:
        # SECDED 10th bit: overall parity across all 9 bits to make the 10-bit block even parity.
        overall_parity = 0
        for bit in code:
            overall_parity ^= bit
        code.append(overall_parity)

    return code


def decode_block(received: list[int], extended: bool | None = None) -> tuple[int, int | None]:
    """Decode a 9-bit or 10-bit block; return (payload, corrected_zero_based_bit_index).

    If extended is True (or auto-detected from a 10-bit input), SECDED error detection
    is enforced: single-bit errors are corrected, and double-bit errors raise DoubleErrorDetected.
    """
    if extended is None:
        extended = len(received) == 10

    expected_len = 10 if extended else 9
    if len(received) != expected_len or any(bit not in (0, 1) for bit in received):
        raise ValueError(f"a block must contain exactly {expected_len} binary bits")

    code = received.copy()

    # Compute Hamming syndrome over positions 1..9 (0-indexed 0..8)
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

    if extended:
        # Check overall parity over all 10 bits
        overall = 0
        for bit in code:
            overall ^= bit

        if syndrome == 0 and overall == 0:
            # Zero errors detected
            corrected = None
        elif syndrome == 0 and overall == 1:
            # Single-bit error in the 10th bit (overall parity bit itself)
            corrected = OVERALL_PARITY_POSITION
            code[OVERALL_PARITY_POSITION] ^= 1
        elif syndrome != 0 and overall == 1:
            # Single-bit error in positions 0..8
            if 1 <= syndrome <= 9:
                corrected = syndrome - 1
                code[corrected] ^= 1
            else:
                raise DoubleErrorDetected(f"uncorrectable multi-bit error (syndrome {syndrome})")
        elif syndrome != 0 and overall == 0:
            # Non-zero syndrome with even overall parity mathematically indicates a double-bit error
            raise DoubleErrorDetected(f"double-bit error detected (syndrome {syndrome})")
    else:
        # Standard Hamming (9,5) single-bit correction
        if 1 <= syndrome <= 9:
            corrected = syndrome - 1
            code[corrected] ^= 1
        # Syndrome above 9 in shortened code is left untouched as outside guaranteed correction

    payload = [code[position] for position in DATA_POSITIONS]
    return bits_to_int(payload), corrected


def bits_to_pulses(bits: list[int]) -> str:
    return "".join("-" if bit else "." for bit in bits)


def pulses_to_bits(pulses: str) -> list[int]:
    if any(symbol not in ".-" for symbol in pulses):
        raise ValueError("pulse blocks may contain only '.' and '-'")
    return [1 if symbol == "-" else 0 for symbol in pulses]


def encode_text(text: str, include_markers: bool = True, extended: bool = False) -> str:
    """Encode supported text to space-separated nine- or ten-pulse blocks."""
    normalized = text.upper()
    unsupported = sorted(set(normalized) - set(SYMBOL_TO_VALUE))
    if unsupported:
        raise ValueError(f"unsupported characters: {unsupported}")

    values = ([START] if include_markers else [])
    values.extend(SYMBOL_TO_VALUE[char] for char in normalized)
    if include_markers:
        values.append(END)
    return " ".join(bits_to_pulses(encode_block(value, extended=extended)) for value in values)


def decode_pulses(stream: str, expect_markers: bool = True, extended: bool | None = None) -> str:
    """Decode a space-separated stream of nine- or ten-pulse blocks."""
    blocks = stream.split()
    if not blocks:
        return ""

    if extended is None:
        extended = len(blocks[0]) == 10

    values = []
    for block in blocks:
        bits = pulses_to_bits(block)
        value, _ = decode_block(bits, extended=extended)
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
