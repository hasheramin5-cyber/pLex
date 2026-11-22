"""Acoustic CW Waveform Synthesizer for PulseLex.

Synthesizes discrete pulse streams into clean, continuous-phase sinusoidal tone
bursts with smooth raised-cosine (Hann) rise/fall envelopes to prevent spectral
splatter and key clicks. Exports standard 16-bit mono PCM WAV audio files using
only the Python Standard Library.
"""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

from .codec import encode_text


def synthesize_tone(
    frequency_hz: float,
    duration_s: float,
    sample_rate: int = 44100,
    amplitude: float = 0.6,
    rise_fall_ms: float = 5.0,
) -> list[float]:
    """Generate a pure sinusoidal tone with Hann-windowed rise and fall edges.

    Applying raised-cosine shaping to the start and end of each tone prevents
    abrupt phase transitions that cause high-frequency key-click artifacts.
    """
    if duration_s <= 0.0:
        return []

    num_samples = int(duration_s * sample_rate)
    samples = [0.0] * num_samples

    # Compute rise/fall boundary sample count
    rf_samples = int((rise_fall_ms / 1000.0) * sample_rate)
    # Ensure rise/fall window does not exceed half the total duration
    rf_samples = min(rf_samples, num_samples // 2)

    two_pi_f = 2.0 * math.pi * frequency_hz

    for i in range(num_samples):
        t = i / sample_rate
        raw_sin = math.sin(two_pi_f * t)

        # Compute envelope scaling
        if rf_samples > 0 and i < rf_samples:
            # Hann ramp-up: 0.5 * (1 - cos(pi * i / rf_samples))
            envelope = 0.5 * (1.0 - math.cos(math.pi * i / rf_samples))
        elif rf_samples > 0 and i >= num_samples - rf_samples:
            # Hann ramp-down: 0.5 * (1 - cos(pi * (num_samples - 1 - i) / rf_samples))
            remaining = num_samples - 1 - i
            envelope = 0.5 * (1.0 - math.cos(math.pi * remaining / rf_samples))
        else:
            envelope = 1.0

        samples[i] = amplitude * envelope * raw_sin

    return samples


def synthesize_silence(duration_s: float, sample_rate: int = 44100) -> list[float]:
    """Generate silent samples for the given duration."""
    if duration_s <= 0.0:
        return []
    return [0.0] * int(duration_s * sample_rate)


def pulse_stream_to_audio(
    stream: str,
    frequency_hz: float = 750.0,
    sample_rate: int = 44100,
    dot_duration_s: float = 0.050,
    inter_element_gap_s: float = 0.020,
    inter_block_pause_s: float = 0.080,
    amplitude: float = 0.6,
) -> list[float]:
    """Convert a PulseLex pulse stream (dots, dashes, spaces) into continuous audio samples.

    Timing rules:
        - '.' (dot): tone active for dot_duration_s, followed by inter_element_gap_s silence.
        - '-' (dash): tone active for 3 * dot_duration_s, followed by inter_element_gap_s silence.
        - ' ' (block pause): silence of inter_block_pause_s.
    """
    samples: list[float] = []
    dash_duration_s = 3.0 * dot_duration_s

    # Add brief lead-in silence (30 ms) to avoid initial audio clipping
    samples.extend(synthesize_silence(0.030, sample_rate))

    for char in stream:
        if char == ".":
            samples.extend(synthesize_tone(frequency_hz, dot_duration_s, sample_rate, amplitude))
            samples.extend(synthesize_silence(inter_element_gap_s, sample_rate))
        elif char == "-":
            samples.extend(synthesize_tone(frequency_hz, dash_duration_s, sample_rate, amplitude))
            samples.extend(synthesize_silence(inter_element_gap_s, sample_rate))
        elif char in (" ", "\t", "\n"):
            samples.extend(synthesize_silence(inter_block_pause_s, sample_rate))

    # Add brief lead-out silence
    samples.extend(synthesize_silence(0.050, sample_rate))
    return samples


def export_wav(
    samples: list[float],
    output_path: str | Path,
    sample_rate: int = 44100,
) -> Path:
    """Export a list of float audio samples (-1.0 to 1.0) to a 16-bit mono PCM WAV file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit PCM (2 bytes per sample)
        wav_file.setframerate(sample_rate)

        # Convert float samples (-1.0 to 1.0) into signed 16-bit integers (-32767 to 32767)
        raw_bytes = bytearray()
        for sample in samples:
            clamped = max(-1.0, min(1.0, sample))
            pcm_val = int(clamped * 32767.0)
            raw_bytes.extend(struct.pack("<h", pcm_val))

        wav_file.writeframes(raw_bytes)

    return path


def text_to_wav(
    text: str,
    output_path: str | Path,
    extended: bool = False,
    frequency_hz: float = 750.0,
    sample_rate: int = 44100,
    dot_duration_s: float = 0.050,
    amplitude: float = 0.6,
) -> Path:
    """Convenience pipeline: encode text, synthesize acoustic pulses, and export WAV file."""
    pulse_stream = encode_text(text, include_markers=True, extended=extended)
    samples = pulse_stream_to_audio(
        pulse_stream,
        frequency_hz=frequency_hz,
        sample_rate=sample_rate,
        dot_duration_s=dot_duration_s,
        amplitude=amplitude,
    )
    return export_wav(samples, output_path, sample_rate=sample_rate)
