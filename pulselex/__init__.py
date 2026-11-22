"""PulseLex: a Morse-inspired error-correcting alphabet with SECDED, continuous deframing, and audio synthesis."""

from .codec import (
    encode_text,
    decode_pulses,
    encode_block,
    decode_block,
    DoubleErrorDetected,
    bits_to_pulses,
    pulses_to_bits,
    ALPHABET,
    START,
    END,
)
from .sync import deframe_pulses, sync_and_decode
from .audio import (
    synthesize_tone,
    synthesize_silence,
    pulse_stream_to_audio,
    export_wav,
    text_to_wav,
)

__all__ = [
    "encode_text",
    "decode_pulses",
    "encode_block",
    "decode_block",
    "DoubleErrorDetected",
    "bits_to_pulses",
    "pulses_to_bits",
    "ALPHABET",
    "START",
    "END",
    "deframe_pulses",
    "sync_and_decode",
    "synthesize_tone",
    "synthesize_silence",
    "pulse_stream_to_audio",
    "export_wav",
    "text_to_wav",
]
