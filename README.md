# 🔎 TextInsight — Text File Analyzer & Report Generator

> A small command-line tool that analyzes `.txt` files, calculates text statistics, finds the most frequent words, estimates reading time, and generates formatted reports.

Built entirely with the **Python standard library** using `collections.Counter`, `re`, `csv`, `pathlib`, and `argparse`.

> 📊 `matplotlib` is optional and used only when the `--chart` flag is enabled.

---

## ✨ Features 

### 🧠 Core

* 📄 Read a `.txt` file with automatic encoding fallback: 
  **UTF-8 / UTF-16 / CP1252 / Latin-1**
* 🔤 Regex tokenizer that keeps `don't` and `well-known` as single words
* 📈 Word frequency table with stopwords filtered out
* 📊 Text statistics:

  * Characters
  * Words
  * Unique words
  * Sentences
  * Paragraphs
  * Average word length
  * Average sentence length
  * Lexical diversity
  * Longest word
* ⏱️ Estimated reading time at a configurable words-per-minute rate
* 📝 Formatted report exported to `data/output/`

### 🚀 Extras

* 📁 Batch processing of a whole folder (`--recursive` for subfolders)
* 📋 Combined `_summary.txt` table when more than one file is processed
* 📑 CSV export of the frequency table (`--csv`)
* 📊 Top-N bar chart as PNG (`--chart`, requires `matplotlib`)
* 🛑 Stopword list loaded from an external file (`--stopwords`)
* 🔢 Minimum word length filter
* ⚙️ Option to turn stopword filtering off entirely

---

## 🛠️ Installation

```bash
git clone https://github.com/<your-username>/textinsight.git
cd textinsight

# Optional — only needed for --chart
pip install -r requirements.txt
```

### Requirements

* 🐍 Python **3.9+**
* 📦 No dependencies required for core features
* 📊 `matplotlib` is optional and only needed for `--chart`

---

## ▶️ Usage

### Analyze a single file

```bash
python src/main.py data/input/sample.txt
```

### Analyze with Top 20 words and CSV export

```bash
python src/main.py data/input/sample.txt --top 20 --csv
```

### Process every `.txt` file in a folder

```bash
python src/main.py data/input --recursive --quiet
```

### Use a custom stopword list and slower reading speed

```bash
python src/main.py data/input/sample.txt --stopwords data/stopwords.txt --wpm 150
```

### Ignore short words and disable stopword filtering

```bash
python src/main.py data/input/sample.txt --no-stopwords --min-length 5
```

### Generate a PNG chart of the top words

```bash
python src/main.py data/input/sample.txt --chart
```

---

## ⚙️ Command-Line Options

| Flag                   | Description                                    |    Default    |
| :--------------------- | :--------------------------------------------- | :-----------: |
| `path`                 | A `.txt` file, or a folder for batch mode      |  **Required** |
| `-o, --output-dir`     | Where reports are written                      | `data/output` |
| `-n, --top N`          | How many top words to include                  |      `10`     |
| `-s, --stopwords FILE` | Stopword list, one word per line               | Built-in list |
| `--no-stopwords`       | Disable stopword filtering                     |      Off      |
| `--min-length N`       | Ignore words shorter than N characters         |      `1`      |
| `--wpm N`              | Reading speed for the time estimate            |     `200`     |
| `--pattern`            | Glob pattern used in folder mode               |    `*.txt`    |
| `-r, --recursive`      | In folder mode, also search subfolders         |      Off      |
| `--csv`                | Also export the frequency table as CSV         |      Off      |
| `--chart`              | Also save a top-words PNG (needs `matplotlib`) |      Off      |
| `-q, --quiet`          | Do not print reports to the console            |      Off      |

### Exit Codes

| Code | Meaning                                                 |
| :--: | :------------------------------------------------------ |
|  `0` | ✅ Success                                               |
|  `1` | ⚠️ Nothing could be analyzed or some files were skipped |
|  `2` | ❌ Invalid arguments                                     |

---

## 📥 Input / 📤 Output Example

### 📄 Input

`data/input/sample.txt`

```text
The Value of Reading

Reading is one of the oldest tools people have for thinking clearly. A book
does not rush the reader. It waits. That patience is exactly what makes reading
different from scrolling, and it is why reading remains useful even in a world
full of faster media.
...
```

### 💻 Command

```bash
python src/main.py data/input/sample.txt --top 8 --csv
```

### 📋 Output

`data/output/sample_report.txt`

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

### 📑 CSV Export

`data/output/sample_frequencies.csv`

```csv
rank,word,count,percent_of_content_words
1,reading,5,4.03
2,read,3,2.42
3,writing,3,2.42
```

### 📁 Batch Mode

`data/output/_summary.txt`

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

## 🗂️ Project Structure

```text
textinsight/
├── src/
│   ├── main.py          # CLI: argument parsing, batch loop, output files
│   └── analyzer.py      # Core logic: tokenizing, stats, report rendering
│
├── data/
│   ├── input/           # Sample .txt files
│   │   ├── sample.txt
│   │   └── notes.txt
│   │
│   ├── output/          # Generated reports (gitignored)
│   └── stopwords.txt    # Editable stopword list
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

## 🔍 How It Works

### 1. 📖 Read

`read_text()` tries several encodings so a file saved from Notepad or Word can still be opened.

**Supported fallback order:**

`UTF-8 → UTF-16 → CP1252 → Latin-1`

---

### 2. 🔤 Tokenize

A regex picks out letter runs while allowing internal apostrophes and hyphens.

Examples:

```text
don't
well-known
```

Tokens are then converted to lowercase.

Digits and punctuation are dropped.

---

### 3. 🔢 Count

`collections.Counter` builds the frequency table over tokens remaining after:

* Stopword filtering
* Minimum-length filtering

Ties are broken alphabetically so results remain reproducible.

---

### 4. 📏 Measure

Text statistics are calculated by analyzing:

* **Sentences** — split on `.`, `!`, `?` and Armenian `։`, `՞`, `՜`
* **Paragraphs** — split on blank lines

---

### 5. 📝 Report

Statistics and a bar-chart-style frequency table are rendered as aligned plain text and written to:

```text
data/output/
```

---

## 🎓 What I Learned

* 📂 Reading and writing files safely with `pathlib`, including encoding fallbacks
* 📊 Aggregating data with dictionaries and `collections.Counter`
* 🔢 Sorting with composite keys to get stable, tie-broken ordering
* 🧩 Splitting a program into a reusable logic module and a thin CLI layer
* 🖥️ Building a real command-line interface with `argparse` and meaningful exit codes
* ✨ Formatting aligned text output with f-string padding

---

## 🚀 Possible Next Steps

* ❤️ Sentiment scoring with a simple word-list approach
* 🔗 N-gram (bigram / trigram) frequency
* 📖 Readability scores such as Flesch–Kincaid
* 🌐 HTML or Markdown report output
* 🧪 Unit tests with `pytest`

---

## 📄 License

MIT
