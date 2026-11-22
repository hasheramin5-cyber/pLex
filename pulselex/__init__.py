"""PulseLex: a Morse-inspired error-correcting alphabet."""

from .codec import encode_text, decode_pulses, encode_block, decode_block

__all__ = ["encode_text", "decode_pulses", "encode_block", "decode_block"]
