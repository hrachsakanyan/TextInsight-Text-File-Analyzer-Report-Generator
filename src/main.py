"""TextInsight command-line interface.

Usage examples:
    python src/main.py data/input/sample.txt
    python src/main.py data/input --recursive --top 15 --csv --chart
    python src/main.py data/input/sample.txt --stopwords data/stopwords.txt
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running both as `python src/main.py` and `python -m src.main`.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from analyzer import (  # type: ignore[no-redef]
        DEFAULT_WPM,
        AnalyzerError,
        analyze_file,
        build_report,
        build_summary,
        collect_files,
        load_stopwords,
        write_chart,
        write_csv,
        write_report,
    )
else:  # pragma: no cover - import style depends on how the script is launched
    from .analyzer import (
        DEFAULT_WPM,
        AnalyzerError,
        analyze_file,
        build_report,
        build_summary,
        collect_files,
        load_stopwords,
        write_chart,
        write_csv,
        write_report,
    )

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "output"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="textinsight",
        description="Analyze .txt files and generate formatted reports.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "path",
        type=Path,
        help="A .txt file, or a folder to process in batch.",
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Where reports are written (default: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "-n", "--top",
        type=int,
        default=10,
        metavar="N",
        help="How many top words to include (default: 10).",
    )
    parser.add_argument(
        "-s", "--stopwords",
        type=Path,
        default=None,
        metavar="FILE",
        help="Stopword list, one word per line. Defaults to the built-in list.",
    )
    parser.add_argument(
        "--no-stopwords",
        action="store_true",
        help="Disable stopword filtering entirely.",
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=1,
        metavar="N",
        help="Ignore words shorter than N characters (default: 1).",
    )
    parser.add_argument(
        "--wpm",
        type=int,
        default=DEFAULT_WPM,
        help=f"Reading speed for the time estimate (default: {DEFAULT_WPM}).",
    )
    parser.add_argument(
        "--pattern",
        default="*.txt",
        help="Glob pattern used in folder mode (default: *.txt).",
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="In folder mode, also search subfolders.",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Also export the word-frequency table as CSV.",
    )
    parser.add_argument(
        "--chart",
        action="store_true",
        help="Also save a top-words bar chart as PNG (requires matplotlib).",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Do not print reports to the console.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.top < 1:
        print("error: --top must be at least 1", file=sys.stderr)
        return 2
    if args.wpm < 1:
        print("error: --wpm must be at least 1", file=sys.stderr)
        return 2

    try:
        stopwords: set[str] = set() if args.no_stopwords else load_stopwords(args.stopwords)
        files = collect_files(args.path, pattern=args.pattern, recursive=args.recursive)
    except AnalyzerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not files:
        print(f"error: no files matching '{args.pattern}' in {args.path}", file=sys.stderr)
        return 1

    all_stats = []
    failures = 0

    for path in files:
        try:
            stats = analyze_file(
                path,
                stopwords=stopwords,
                top_n=args.top,
                wpm=args.wpm,
                min_word_length=args.min_length,
            )
        except AnalyzerError as exc:
            print(f"warning: skipping {path.name}: {exc}", file=sys.stderr)
            failures += 1
            continue

        all_stats.append(stats)
        stem = path.stem

        report_path = write_report(stats, args.output_dir / f"{stem}_report.txt", wpm=args.wpm)
        written = [report_path]

        if args.csv:
            written.append(write_csv(stats, args.output_dir / f"{stem}_frequencies.csv"))

        if args.chart:
            try:
                written.append(write_chart(stats, args.output_dir / f"{stem}_top_words.png"))
            except AnalyzerError as exc:
                print(f"warning: {exc}", file=sys.stderr)

        if not args.quiet:
            print(build_report(stats, wpm=args.wpm))
        for output in written:
            print(f"[saved] {output}")

    if len(all_stats) > 1:
        summary = build_summary(all_stats, wpm=args.wpm)
        summary_path = args.output_dir / "_summary.txt"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(summary, encoding="utf-8")
        if not args.quiet:
            print()
            print(summary)
        print(f"[saved] {summary_path}")

    if not all_stats:
        return 1
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
