"""Command-line interface for score transposition and conversion."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from . import __version__
from .mscz import transpose_mscz
from .tools import convert_score
from .workflows import recognize_pdf_with_smartscore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="music-score",
        description="Transpose MuseScore files and run explicit desktop conversion workflows.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    transpose = commands.add_parser("transpose", help="Transpose an MSCZ score.")
    transpose.add_argument("input", type=Path)
    transpose.add_argument("output", type=Path)
    transpose.add_argument("--from-key", required=True)
    transpose.add_argument("--to-key", required=True)
    transpose.add_argument(
        "--allow-pitch-clipping",
        action="store_true",
        help="Clip pitches outside MIDI 0..127 instead of aborting.",
    )
    transpose.add_argument(
        "--export-pdf",
        type=Path,
        help="After transposition, ask MuseScore to create this PDF.",
    )

    convert = commands.add_parser("convert", help="Convert a score through MuseScore 4.")
    convert.add_argument("input", type=Path)
    convert.add_argument("output", type=Path)

    recognize = commands.add_parser(
        "recognize",
        help="Launch SmartScore for manual PDF recognition, then create MSCZ.",
    )
    recognize.add_argument("pdf", type=Path)
    recognize.add_argument("output_directory", type=Path)
    recognize.add_argument("--timeout", type=float)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "transpose":
            report = transpose_mscz(
                args.input,
                args.output,
                args.from_key,
                args.to_key,
                strict_pitch_range=not args.allow_pitch_clipping,
            )
            if args.export_pdf:
                convert_score(args.output, args.export_pdf)
            print(json.dumps(asdict(report), indent=2))
        elif args.command == "convert":
            print(convert_score(args.input, args.output))
        else:
            print(
                recognize_pdf_with_smartscore(
                    args.pdf,
                    args.output_directory,
                    timeout=args.timeout,
                )
            )
    except (FileNotFoundError, RuntimeError, ValueError, TimeoutError) as exc:
        print(f"music-score: error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

