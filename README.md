# TextInsight — Text File Analyzer & Report Generator

A small command-line tool that reads `.txt` files, computes word / character /
sentence statistics, finds the most frequent words (with stopwords removed),
estimates reading time, and writes a formatted report file.

Built with the Python standard library only — `collections.Counter`, `re`,
`csv`, `pathlib`, `argparse`. `matplotlib` is optional and used only by the
`--chart` flag.

---

## Features

**Core**

- Read a `.txt` file with automatic encoding fallback (UTF-8 / UTF-16 / CP1252 / Latin-1)
- Regex tokenizer that keeps `don't` and `well-known` as single words
- Word frequency table with stopwords filtered out
- Text statistics: characters, words, unique words, sentences, paragraphs,
  average word length, average sentence length, lexical diversity, longest word
- Estimated reading time at a configurable words-per-minute rate
- Formatted report exported to `data/output/`

**Extras**

- Batch processing of a whole folder (`--recursive` for subfolders)
- Combined `_summary.txt` table when more than one file is processed
- CSV export of the frequency table (`--csv`)
- Top-N bar chart as PNG (`--chart`, needs matplotlib)
- Stopword list loaded from an external file (`--stopwords`)
- Minimum word length filter, or stopword filtering turned off entirely

---

## Installation

```bash
git clone https://github.com/<your-username>/textinsight.git
cd textinsight

# Optional -- only needed for --chart
pip install -r requirements.txt
```

Requires Python 3.9 or newer. No dependencies for the core features.

---

## Usage

```bash
# Analyze a single file
python src/main.py data/input/sample.txt

# Top 20 words, plus a CSV export
python src/main.py data/input/sample.txt --top 20 --csv

# Process every .txt in a folder, quietly, and write a summary
python src/main.py data/input --recursive --quiet

# Use your own stopword list and a slower reading speed
python src/main.py data/input/sample.txt --stopwords data/stopwords.txt --wpm 150

# Ignore short words and skip stopword filtering
python src/main.py data/input/sample.txt --no-stopwords --min-length 5

# Save a PNG bar chart of the top words
python src/main.py data/input/sample.txt --chart
```

### Options

| Flag | Description | Default |
| --- | --- | --- |
| `path` | A `.txt` file, or a folder for batch mode | *(required)* |
| `-o, --output-dir` | Where reports are written | `data/output` |
| `-n, --top N` | How many top words to include | `10` |
| `-s, --stopwords FILE` | Stopword list, one word per line | built-in list |
| `--no-stopwords` | Disable stopword filtering | off |
| `--min-length N` | Ignore words shorter than N characters | `1` |
| `--wpm N` | Reading speed for the time estimate | `200` |
| `--pattern` | Glob pattern used in folder mode | `*.txt` |
| `-r, --recursive` | In folder mode, also search subfolders | off |
| `--csv` | Also export the frequency table as CSV | off |
| `--chart` | Also save a top-words PNG (needs matplotlib) | off |
| `-q, --quiet` | Do not print reports to the console | off |

Exit codes: `0` success, `1` nothing could be analyzed or some files were
skipped, `2` invalid arguments.

---

## Input / Output example

**Input** — `data/input/sample.txt`

```text
The Value of Reading

Reading is one of the oldest tools people have for thinking clearly. A book
does not rush the reader. It waits. That patience is exactly what makes reading
different from scrolling, and it is why reading remains useful even in a world
full of faster media.
...
```

**Command**

```bash
python src/main.py data/input/sample.txt --top 8 --csv
```

**Output** — `data/output/sample_report.txt`

```text
============================================================
============== TextInsight Report: sample.txt ==============
============================================================

Source file : data/input/sample.txt

------------------------------------------------------------
TEXT STATISTICS
------------------------------------------------------------
Characters (with spaces)         : 1,240
Characters (no spaces)           : 1,023
Words                            : 212
Unique words                     : 135
Sentences                        : 20
Paragraphs                       : 6
Average word length              : 4.69 chars
Average sentence length          : 10.60 words
Lexical diversity                : 63.7%
Longest word                     : understanding
Stopwords filtered out           : 88
Estimated reading time (200 wpm) : 1 min 4 sec

------------------------------------------------------------
TOP 8 WORDS (stopwords excluded)
------------------------------------------------------------
 1. reading        5    4.0%  ##############################
 2. read           3    2.4%  ##################
 3. writing        3    2.4%  ##################
 4. attention      2    1.6%  ############
 5. draft          2    1.6%  ############
 6. enough         2    1.6%  ############
 7. fact           2    1.6%  ############
 8. feeling        2    1.6%  ############

============================================================
Generated by TextInsight
============================================================
```

**Output** — `data/output/sample_frequencies.csv`

```csv
rank,word,count,percent_of_content_words
1,reading,5,4.03
2,read,3,2.42
3,writing,3,2.42
```

**Batch mode** — `data/output/_summary.txt`

```text
==============================================================================
=============================== BATCH SUMMARY ================================
==============================================================================

File                              Words  Sentences  Avg len      Reading
------------------------------------------------------------------------
notes.txt                           151         15     4.29       45 sec
sample.txt                          212         20     4.69  1 min 4 sec
------------------------------------------------------------------------
TOTAL (2 files)                     363         35          1 min 49 sec
```

---

## Project structure

```text
textinsight/
├── src/
│   ├── main.py          # CLI: argument parsing, batch loop, output files
│   └── analyzer.py      # Core logic: tokenizing, stats, report rendering
├── data/
│   ├── input/           # Sample .txt files
│   │   ├── sample.txt
│   │   └── notes.txt
│   ├── output/          # Generated reports (gitignored)
│   └── stopwords.txt    # Editable stopword list
├── README.md
├── requirements.txt
└── .gitignore
```

---

## How it works

1. **Read** — `read_text()` tries several encodings so a file saved from
   Notepad or Word still opens.
2. **Tokenize** — a regex picks out letter runs, allowing internal apostrophes
   and hyphens, then lowercases them. Digits and punctuation are dropped.
3. **Count** — `collections.Counter` builds the frequency table over the tokens
   left after stopword and minimum-length filtering. Ties are broken
   alphabetically so results are reproducible.
4. **Measure** — sentences are found by splitting on `.`, `!`, `?` (and the
   Armenian `։`, `՞`, `՜`); paragraphs by splitting on blank lines.
5. **Report** — statistics and a bar-chart-style frequency table are rendered
   as aligned plain text and written to `data/output/`.

---

## What I learned

- Reading and writing files safely with `pathlib`, including encoding fallbacks
- Aggregating data with dictionaries and `collections.Counter`
- Sorting with composite keys to get stable, tie-broken ordering
- Splitting a program into a reusable logic module and a thin CLI layer
- Building a real command-line interface with `argparse` and meaningful exit codes
- Formatting aligned text output with f-string padding

---

## Possible next steps

- Sentiment scoring with a simple word-list approach
- N-gram (bigram / trigram) frequency
- Readability scores such as Flesch–Kincaid
- HTML or Markdown report output
- Unit tests with `pytest`

---

## License

MIT
