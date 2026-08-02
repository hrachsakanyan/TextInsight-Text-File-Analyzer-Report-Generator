"""Core text analysis logic for TextInsight.

Pure functions + a small dataclass holding the results.  Nothing in here
touches the CLI, so the module stays easy to test and reuse.
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

# Average adult silent reading speed, words per minute.
DEFAULT_WPM = 200

# Fallback stopword list, used when no external file is supplied.
DEFAULT_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an",
    "and", "any", "are", "as", "at", "be", "because", "been", "before",
    "being", "below", "between", "both", "but", "by", "can", "did", "do",
    "does", "doing", "don", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "he", "her", "here", "hers",
    "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is",
    "it", "its", "itself", "just", "me", "more", "most", "my", "myself",
    "no", "nor", "not", "now", "of", "off", "on", "once", "only", "or",
    "other", "our", "ours", "ourselves", "out", "over", "own", "s", "same",
    "she", "should", "so", "some", "such", "t", "than", "that", "the",
    "their", "theirs", "them", "themselves", "then", "there", "these",
    "they", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "we", "were", "what", "when", "where", "which", "while",
    "who", "whom", "why", "will", "with", "you", "your", "yours", "yourself",
    "yourselves",
}

# A "word" is a letter run that may contain internal apostrophes or hyphens,
# so "don't" and "well-known" survive tokenization intact.
WORD_RE = re.compile(r"[A-Za-zÀ-ɏ԰-֏]+(?:['’-][A-Za-zÀ-ɏ԰-֏]+)*")

# Sentence terminators: ., !, ?, Armenian ':' (verjaket) and '՞', '՜'.
SENTENCE_SPLIT_RE = re.compile(r"[.!?։՞՜]+[\s\"'”’)\]]*|\n{2,}")

# Encodings tried in order when reading a file.
ENCODINGS = ("utf-8-sig", "utf-16", "cp1252", "latin-1")


class AnalyzerError(Exception):
    """Raised when a file cannot be read or analyzed."""


@dataclass
class TextStats:
    """Everything the report generator needs about a single file."""

    source: Path
    char_count: int
    char_count_no_spaces: int
    word_count: int
    unique_word_count: int
    sentence_count: int
    paragraph_count: int
    avg_word_length: float
    avg_sentence_length: float
    reading_time_minutes: float
    longest_word: str
    top_words: list[tuple[str, int]] = field(default_factory=list)
    stopwords_removed: int = 0

    @property
    def lexical_diversity(self) -> float:
        """Unique words / total words -- a rough vocabulary richness score."""
        if self.word_count == 0:
            return 0.0
        return self.unique_word_count / self.word_count


def read_text(path: Path) -> str:
    """Read a text file, trying a few common encodings before giving up."""
    if not path.is_file():
        raise AnalyzerError(f"Not a file: {path}")

    last_error: Exception | None = None
    for encoding in ENCODINGS:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError as exc:
            last_error = exc
        except OSError as exc:
            raise AnalyzerError(f"Could not read {path}: {exc}") from exc

    raise AnalyzerError(f"Could not decode {path} with any of {ENCODINGS}: {last_error}")


def load_stopwords(path: Path | None) -> set[str]:
    """Load stopwords from a file (one per line, '#' comments allowed).

    Returns the built-in list when no path is given.
    """
    if path is None:
        return set(DEFAULT_STOPWORDS)

    raw = read_text(path)
    words = set()
    for line in raw.splitlines():
        line = line.split("#", 1)[0].strip().lower()
        if line:
            words.add(line)
    return words


def tokenize(text: str) -> list[str]:
    """Split text into lowercase word tokens, dropping punctuation and digits."""
    return [match.group(0).lower() for match in WORD_RE.finditer(text)]


def count_sentences(text: str) -> int:
    """Count sentences by splitting on terminal punctuation."""
    stripped = text.strip()
    if not stripped:
        return 0

    pieces = [piece for piece in SENTENCE_SPLIT_RE.split(stripped) if piece and piece.strip()]
    # Text ending without punctuation still holds one trailing sentence, which
    # split() already leaves as a final piece -- so the piece count is the answer.
    return max(len(pieces), 1)


def count_paragraphs(text: str) -> int:
    """Count paragraphs as blocks separated by one or more blank lines."""
    blocks = [block for block in re.split(r"\n\s*\n", text) if block.strip()]
    return len(blocks)


def analyze_text(
    text: str,
    source: Path,
    stopwords: set[str] | None = None,
    top_n: int = 10,
    wpm: int = DEFAULT_WPM,
    min_word_length: int = 1,
) -> TextStats:
    """Compute every statistic for one chunk of text."""
    stopwords = stopwords if stopwords is not None else set(DEFAULT_STOPWORDS)

    tokens = tokenize(text)
    kept = [
        word for word in tokens
        if word not in stopwords and len(word) >= min_word_length
    ]

    word_count = len(tokens)
    total_letters = sum(len(word) for word in tokens)
    sentence_count = count_sentences(text)

    counter = Counter(kept)
    # Sort by descending frequency, then alphabetically so ties are stable.
    top_words = sorted(counter.items(), key=lambda item: (-item[1], item[0]))[:top_n]

    return TextStats(
        source=source,
        char_count=len(text),
        char_count_no_spaces=len(re.sub(r"\s", "", text)),
        word_count=word_count,
        unique_word_count=len(set(tokens)),
        sentence_count=sentence_count,
        paragraph_count=count_paragraphs(text),
        avg_word_length=(total_letters / word_count) if word_count else 0.0,
        avg_sentence_length=(word_count / sentence_count) if sentence_count else 0.0,
        reading_time_minutes=(word_count / wpm) if wpm > 0 else 0.0,
        longest_word=max(tokens, key=len) if tokens else "",
        top_words=top_words,
        stopwords_removed=word_count - len(kept),
    )


def analyze_file(path: Path, **kwargs) -> TextStats:
    """Read a file from disk and analyze it."""
    return analyze_text(read_text(path), source=path, **kwargs)


def format_reading_time(minutes: float) -> str:
    """Turn a float number of minutes into '2 min 30 sec'."""
    total_seconds = int(round(minutes * 60))
    if total_seconds < 60:
        return f"{total_seconds} sec"
    mins, secs = divmod(total_seconds, 60)
    if secs == 0:
        return f"{mins} min"
    return f"{mins} min {secs} sec"


def _bar(value: int, maximum: int, width: int = 30) -> str:
    """Draw a simple text bar for the frequency table."""
    if maximum <= 0:
        return ""
    filled = max(1, round(value / maximum * width))
    return "#" * filled


def build_report(stats: TextStats, wpm: int = DEFAULT_WPM) -> str:
    """Render a human-readable report for one file."""
    lines: list[str] = []
    title = f" TextInsight Report: {stats.source.name} "
    lines.append("=" * 60)
    lines.append(title.center(60, "="))
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Source file : {stats.source}")
    lines.append("")

    lines.append("-" * 60)
    lines.append("TEXT STATISTICS")
    lines.append("-" * 60)
    rows = [
        ("Characters (with spaces)", f"{stats.char_count:,}"),
        ("Characters (no spaces)", f"{stats.char_count_no_spaces:,}"),
        ("Words", f"{stats.word_count:,}"),
        ("Unique words", f"{stats.unique_word_count:,}"),
        ("Sentences", f"{stats.sentence_count:,}"),
        ("Paragraphs", f"{stats.paragraph_count:,}"),
        ("Average word length", f"{stats.avg_word_length:.2f} chars"),
        ("Average sentence length", f"{stats.avg_sentence_length:.2f} words"),
        ("Lexical diversity", f"{stats.lexical_diversity:.1%}"),
        ("Longest word", stats.longest_word or "-"),
        ("Stopwords filtered out", f"{stats.stopwords_removed:,}"),
        (f"Estimated reading time ({wpm} wpm)", format_reading_time(stats.reading_time_minutes)),
    ]
    label_width = max(len(label) for label, _ in rows)
    for label, value in rows:
        lines.append(f"{label.ljust(label_width)} : {value}")
    lines.append("")

    lines.append("-" * 60)
    lines.append(f"TOP {len(stats.top_words)} WORDS (stopwords excluded)")
    lines.append("-" * 60)
    if not stats.top_words:
        lines.append("(no words found)")
    else:
        max_count = stats.top_words[0][1]
        word_width = max(len(word) for word, _ in stats.top_words)
        content_words = stats.word_count - stats.stopwords_removed
        for rank, (word, count) in enumerate(stats.top_words, start=1):
            share = (count / content_words * 100) if content_words else 0.0
            lines.append(
                f"{rank:>2}. {word.ljust(word_width)}  {count:>5}  "
                f"{share:>5.1f}%  {_bar(count, max_count)}"
            )
    lines.append("")
    lines.append("=" * 60)
    lines.append("Generated by TextInsight")
    lines.append("=" * 60)

    return "\n".join(lines) + "\n"


def write_report(stats: TextStats, output_path: Path, wpm: int = DEFAULT_WPM) -> Path:
    """Write the formatted report to disk and return the path written."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_report(stats, wpm=wpm), encoding="utf-8")
    return output_path


def write_csv(stats: TextStats, output_path: Path) -> Path:
    """Export the word-frequency table as CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    content_words = stats.word_count - stats.stopwords_removed
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["rank", "word", "count", "percent_of_content_words"])
        for rank, (word, count) in enumerate(stats.top_words, start=1):
            share = (count / content_words * 100) if content_words else 0.0
            writer.writerow([rank, word, count, f"{share:.2f}"])
    return output_path


def write_chart(stats: TextStats, output_path: Path) -> Path:
    """Save a horizontal bar chart of the top words (needs matplotlib)."""
    try:
        import matplotlib
        matplotlib.use("Agg")  # headless backend -- no display needed
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise AnalyzerError(
            "matplotlib is not installed. Install it with: pip install matplotlib"
        ) from exc

    if not stats.top_words:
        raise AnalyzerError("No words to chart.")

    words = [word for word, _ in stats.top_words][::-1]
    counts = [count for _, count in stats.top_words][::-1]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, max(3, 0.4 * len(words) + 1.5)))
    ax.barh(words, counts, color="#4C78A8")
    ax.set_xlabel("Occurrences")
    ax.set_title(f"Top {len(words)} words - {stats.source.name}")
    for index, count in enumerate(counts):
        ax.text(count, index, f" {count}", va="center", fontsize=9)
    ax.margins(x=0.12)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def collect_files(target: Path, pattern: str = "*.txt", recursive: bool = False) -> list[Path]:
    """Return the list of text files to process for a file or folder target."""
    if target.is_file():
        return [target]
    if target.is_dir():
        globber = target.rglob if recursive else target.glob
        return sorted(path for path in globber(pattern) if path.is_file())
    raise AnalyzerError(f"Path does not exist: {target}")


def build_summary(all_stats: list[TextStats], wpm: int = DEFAULT_WPM) -> str:
    """Render a combined overview table for a batch run."""
    lines = ["=" * 78, " BATCH SUMMARY ".center(78, "="), "=" * 78, ""]
    header = f"{'File':<30} {'Words':>8} {'Sentences':>10} {'Avg len':>8} {'Reading':>12}"
    lines.append(header)
    lines.append("-" * len(header))
    for stats in all_stats:
        name = stats.source.name
        if len(name) > 30:
            name = name[:27] + "..."
        lines.append(
            f"{name:<30} {stats.word_count:>8,} {stats.sentence_count:>10,} "
            f"{stats.avg_word_length:>8.2f} {format_reading_time(stats.reading_time_minutes):>12}"
        )
    lines.append("-" * len(header))

    total_words = sum(stats.word_count for stats in all_stats)
    total_sentences = sum(stats.sentence_count for stats in all_stats)
    total_minutes = total_words / wpm if wpm > 0 else 0.0
    lines.append(
        f"{'TOTAL (' + str(len(all_stats)) + ' files)':<30} {total_words:>8,} "
        f"{total_sentences:>10,} {'':>8} {format_reading_time(total_minutes):>12}"
    )
    lines.append("")
    return "\n".join(lines) + "\n"
