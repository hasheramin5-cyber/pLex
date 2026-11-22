"""Command-line interface for PulseLex."""

import argparse
from .codec import encode_text, decode_pulses


def main() -> None:
    parser = argparse.ArgumentParser(prog="pulselex", description="Morse-inspired error-correcting alphabet")
    sub = parser.add_subparsers(dest="command", required=True)
    encode_parser = sub.add_parser("encode", help="encode text into dot/dash blocks")
    encode_parser.add_argument("text")
    decode_parser = sub.add_parser("decode", help="decode dot/dash blocks")
    decode_parser.add_argument("stream")
    args = parser.parse_args()

    if args.command == "encode":
        print(encode_text(args.text))
    else:
        print(decode_pulses(args.stream))


if __name__ == "__main__":
    main()
