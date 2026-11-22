"""Tests for Acoustic CW Waveform Synthesizer."""

import pytest
import wave
from pathlib import Path
from pulselex.audio import (
    synthesize_tone,
    synthesize_silence,
    pulse_stream_to_audio,
    export_wav,
    text_to_wav,
)


def test_synthesize_tone_sample_count_and_amplitude():
    sample_rate = 8000
    duration_s = 0.100
    freq = 600.0
    amp = 0.5
    samples = synthesize_tone(freq, duration_s, sample_rate=sample_rate, amplitude=amp)

    expected_samples = int(duration_s * sample_rate)
    assert len(samples) == expected_samples

    # Verify peak sample does not exceed target amplitude
    assert max(abs(s) for s in samples) <= amp + 1e-6
    # Verify smooth envelope: first and last samples should be close to 0 due to Hann window
    assert abs(samples[0]) < 0.05
    assert abs(samples[-1]) < 0.05


def test_synthesize_tone_zero_or_negative_duration():
    assert synthesize_tone(750.0, 0.0) == []
    assert synthesize_tone(750.0, -0.5) == []


def test_synthesize_tone_invalid_parameters():
    with pytest.raises(ValueError, match="frequency_hz must be positive"):
        synthesize_tone(-100.0, 0.1)
    with pytest.raises(ValueError, match="sample_rate must be positive"):
        synthesize_tone(750.0, 0.1, sample_rate=0)
    with pytest.raises(ValueError, match="amplitude must be between"):
        synthesize_tone(750.0, 0.1, amplitude=1.5)


def test_synthesize_silence():
    sample_rate = 16000
    duration_s = 0.05
    silence = synthesize_silence(duration_s, sample_rate=sample_rate)
    assert len(silence) == int(duration_s * sample_rate)
    assert all(s == 0.0 for s in silence)
    assert synthesize_silence(0.0) == []
    with pytest.raises(ValueError, match="sample_rate must be positive"):
        synthesize_silence(0.1, sample_rate=-1)


def test_pulse_stream_to_audio():
    sample_rate = 8000
    stream = ".- "
    samples = pulse_stream_to_audio(
        stream,
        frequency_hz=700.0,
        sample_rate=sample_rate,
        dot_duration_s=0.040,
        inter_element_gap_s=0.020,
        inter_block_pause_s=0.060,
    )
    assert len(samples) > 0
    assert any(s != 0.0 for s in samples)


def test_pulse_stream_to_audio_invalid_dot_duration():
    with pytest.raises(ValueError, match="dot_duration_s must be positive"):
        pulse_stream_to_audio("...", dot_duration_s=0.0)


def test_export_wav_file_structure(tmp_path: Path):
    sample_rate = 16000
    samples = [0.1 * i for i in range(10)]
    out_file = tmp_path / "test_out.wav"
    exported = export_wav(samples, out_file, sample_rate=sample_rate)

    assert exported.exists()
    assert exported.stat().st_size > 44  # WAV header is 44 bytes

    with wave.open(str(exported), "rb") as wav_in:
        assert wav_in.getnchannels() == 1  # Mono
        assert wav_in.getsampwidth() == 2  # 16-bit
        assert wav_in.getframerate() == sample_rate
        assert wav_in.getnframes() == len(samples)


def test_text_to_wav_pipeline(tmp_path: Path):
    out_file = tmp_path / "telemetry.wav"
    result_path = text_to_wav("OK", out_file, sample_rate=8000, dot_duration_s=0.020)
    assert result_path.exists()

    with wave.open(str(result_path), "rb") as wav_in:
        assert wav_in.getnchannels() == 1
        assert wav_in.getframerate() == 8000
        assert wav_in.getnframes() > 100
