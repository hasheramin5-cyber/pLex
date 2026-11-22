"""Comprehensive unit tests for the PulseLex command-line interface."""

import pytest
from pathlib import Path
from pulselex.cli import build_parser, run_cli, main
from pulselex.codec import encode_text


def test_cli_encode_standard(capsys):
    parser = build_parser()
    args = parser.parse_args(["encode", "HELLO"])
    code = run_cli(args)
    assert code == 0
    captured = capsys.readouterr()
    assert len(captured.out.strip().split()) == 7  # START + 5 chars + END


def test_cli_encode_extended(capsys):
    parser = build_parser()
    args = parser.parse_args(["encode", "--extended", "HI"])
    code = run_cli(args)
    assert code == 0
    captured = capsys.readouterr()
    blocks = captured.out.strip().split()
    assert len(blocks) == 4
    for b in blocks:
        assert len(b) == 10  # 10-bit SECDED


def test_cli_encode_no_markers(capsys):
    parser = build_parser()
    args = parser.parse_args(["encode", "--no-markers", "AB"])
    code = run_cli(args)
    assert code == 0
    captured = capsys.readouterr()
    blocks = captured.out.strip().split()
    assert len(blocks) == 2  # No START/END


def test_cli_decode_standard(capsys):
    stream = encode_text("WORLD")
    parser = build_parser()
    args = parser.parse_args(["decode", stream])
    code = run_cli(args)
    assert code == 0
    captured = capsys.readouterr()
    assert captured.out.strip() == "WORLD"


def test_cli_decode_no_markers(capsys):
    stream = encode_text("CODE", include_markers=False)
    parser = build_parser()
    args = parser.parse_args(["decode", "--no-markers", stream])
    code = run_cli(args)
    assert code == 0
    captured = capsys.readouterr()
    assert captured.out.strip() == "CODE"


def test_cli_sync_decode(capsys):
    stream = encode_text("SYNC").replace(" ", "")
    noisy = "..noise.." + stream + "--noise--"
    parser = build_parser()
    args = parser.parse_args(["sync-decode", noisy, "--verbose"])
    code = run_cli(args)
    assert code == 0
    captured = capsys.readouterr()
    assert "SYNC" in captured.out
    assert "--- Framing Metadata ---" in captured.out


def test_cli_audio_export(tmp_path: Path, capsys):
    out_wav = tmp_path / "cli_test.wav"
    parser = build_parser()
    args = parser.parse_args(["audio", "SOS", "-o", str(out_wav), "--dot-duration", "0.02"])
    code = run_cli(args)
    assert code == 0
    captured = capsys.readouterr()
    assert "Exported PulseLex audio" in captured.out
    assert out_wav.exists()


def test_cli_unsupported_character_error(capsys):
    parser = build_parser()
    args = parser.parse_args(["encode", "INVALID#123"])
    code = run_cli(args)
    assert code == 1
    captured = capsys.readouterr()
    assert "pulselex error:" in captured.err


def test_cli_main_exit_code(capsys):
    # Calling main with invalid character should trigger sys.exit(1)
    with pytest.raises(SystemExit) as exc_info:
        main(["encode", "ILLEGAL!"])
    assert exc_info.value.code == 1
