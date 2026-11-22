"""Command-line interface for PulseLex."""

import argparse
from pathlib import Path
from .codec import encode_text, decode_pulses
from .sync import deframe_pulses, sync_and_decode
from .audio import text_to_wav, pulse_stream_to_audio, export_wav


def main() -> None:
    parser = argparse.ArgumentParser(prog="pulselex", description="Morse-inspired error-correcting alphabet")
    sub = parser.add_subparsers(dest="command", required=True)

    # Encode subcommand
    encode_parser = sub.add_parser("encode", help="encode text into dot/dash blocks")
    encode_parser.add_argument("text", help="ASCII text to encode")
    encode_parser.add_argument("--extended", action="store_true", help="enable 10-bit SECDED mode")
    encode_parser.add_argument("--no-markers", action="store_true", help="omit START and END markers")

    # Decode subcommand
    decode_parser = sub.add_parser("decode", help="decode space-separated dot/dash blocks")
    decode_parser.add_argument("stream", help="space-separated pulse stream")
    decode_parser.add_argument("--extended", action="store_true", default=None, help="force 10-bit SECDED decoding")
    decode_parser.add_argument("--no-markers", action="store_true", help="do not expect START and END markers")

    # Synchronize and Deframe subcommand (continuous streams)
    sync_parser = sub.add_parser("sync-decode", help="synchronize and deframe continuous or noisy pulse streams")
    sync_parser.add_argument("stream", help="continuous pulse stream (with or without whitespace)")
    sync_parser.add_argument("--extended", action="store_true", default=False, help="expect 10-bit SECDED blocks")
    sync_parser.add_argument("--max-start-dist", type=int, default=1, help="maximum Hamming distance for START marker")
    sync_parser.add_argument("--lenient", action="store_true", help="continue on uncorrectable errors, inserting '?'")
    sync_parser.add_argument("--verbose", action="store_true", help="print synchronization and correction metadata")

    # Audio synthesis subcommand
    audio_parser = sub.add_parser("audio", help="synthesize pulse audio and export WAV file")
    audio_parser.add_argument("text", help="text message to synthesize into audio")
    audio_parser.add_argument("-o", "--output", default="pulselex_audio.wav", help="output WAV filename (default: pulselex_audio.wav)")
    audio_parser.add_argument("--extended", action="store_true", help="use 10-bit SECDED blocks")
    audio_parser.add_argument("--freq", type=float, default=750.0, help="tone frequency in Hz (default: 750.0)")
    audio_parser.add_argument("--dot-duration", type=float, default=0.050, help="dot duration in seconds (default: 0.050)")

    args = parser.parse_args()

    if args.command == "encode":
        include_markers = not args.no_markers
        print(encode_text(args.text, include_markers=include_markers, extended=args.extended))

    elif args.command == "decode":
        expect_markers = not args.no_markers
        print(decode_pulses(args.stream, expect_markers=expect_markers, extended=args.extended))

    elif args.command == "sync-decode":
        strict = not args.lenient
        text, meta = deframe_pulses(
            args.stream,
            extended=args.extended,
            max_start_distance=args.max_start_dist,
            strict=strict,
        )
        print(text)
        if args.verbose:
            print("--- Framing Metadata ---")
            for k, v in meta.items():
                print(f"{k}: {v}")

    elif args.command == "audio":
        out_path = text_to_wav(
            args.text,
            args.output,
            extended=args.extended,
            frequency_hz=args.freq,
            dot_duration_s=args.dot_duration,
        )
        print(f"Exported PulseLex audio: {out_path}")


if __name__ == "__main__":
    main()
