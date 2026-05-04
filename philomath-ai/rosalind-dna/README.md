# Rosalind DNA Basics — Sessions 1–2

> **Part of [Philomath AI](../README.md)**

These are the foundational Rosalind problems that form **Sessions 1–2** of
the Philomath live problem-solving series.  They introduce the core building
blocks of bioinformatics: representing DNA as strings, manipulating sequences
at the character level, and extracting the first meaningful statistics from
raw sequence data.

---

## 📚 Problems Covered

| # | Problem | Rosalind ID | Topic |
|---|---------|-------------|-------|
| 1 | [Counting DNA Nucleotides](#1-dna--counting-dna-nucleotides) | [DNA](https://rosalind.info/problems/dna/) | Base counting, dictionaries |
| 2 | [Reverse Complement](#2-revc--reverse-complement) | [REVC](https://rosalind.info/problems/revc/) | Watson-Crick pairing, string reversal |
| 3 | [Computing GC Content](#3-gc--computing-gc-content) | [GC](https://rosalind.info/problems/gc/) | GC content, FASTA parsing, argmax |

---

## 🧬 Problem Explanations

### 1. DNA — Counting DNA Nucleotides

**Concept:** DNA is a string over the four-letter alphabet {A, C, G, T}.
Counting the frequency of each nucleotide is the simplest possible sequence
statistic — and the foundation for everything else in bioinformatics.

**Problem:** Given a DNA string, output four integers counting the occurrences
of A, C, G, and T (in that order).

**Key functions:**
- `count_nucleotides(dna)` — returns a dict `{'A': …, 'C': …, 'G': …, 'T': …}`
- `format_counts(counts)` — formats the dict as `"A C G T"` space-separated string

**Sample:**

```
Input:  AGCTTTTCATTCTGACTGCAACGGGCAATATGTCTCTGTGTGGATTAAAAAAAGAGTGTCTGATAGCAGC
Output: 20 12 17 21
```

---

### 2. REVC — Reverse Complement

**Concept:** DNA is a double helix with two antiparallel strands held together
by Watson-Crick base pairs:

| Base | Complement |
|------|------------|
| A    | T          |
| T    | A          |
| C    | G          |
| G    | C          |

To describe the complementary strand in the conventional 5'→3' direction we
must **complement** every base and then **reverse** the result.

**Problem:** Given a DNA string s, return its reverse complement.

**Key functions:**
- `complement(base)` — returns the complement of a single nucleotide
- `reverse_complement(dna)` — returns the full reverse complement

**Sample:**

```
Input:  AAAACCCGGT
Output: ACCGGGTTTT
```

**Note:** Many important biological sequences are **palindromes** — equal to
their own reverse complement (e.g., the EcoRI restriction site GAATTC).

---

### 3. GC — Computing GC Content

**Concept:** The **GC content** of a DNA sequence is the fraction of bases
that are G or C.  G–C pairs are held by three hydrogen bonds (vs. two for
A–T), so GC-rich sequences are more thermodynamically stable.  GC content
varies significantly across organisms and is used in species identification,
primer design, and quality control.

**Problem:** Given a FASTA file with multiple DNA sequences, find the record
with the highest GC content and report its ID along with the percentage.

**Key functions:**
- `gc_content(dna)` — returns GC fraction as a float in [0, 1]
- `parse_fasta(text)` — parses FASTA text to `{label: sequence}` dict
- `highest_gc(fasta_text)` — returns `(label, gc_percentage)` for the winner

**Sample FASTA:**

```
>Rosalind_6404
CCTGCGGAAGATCGGCACTAGAATAGCCAGAACCGTTTCTCTGAGTTTACGCTTT
>Rosalind_5959
CCATCGGTAGCGCATCCTTAGTCCAATTAAGTCCCTATCCAGGCGCTCCGCCGAAGGTCTATATCCATTT
>Rosalind_0808
CCACCCTCGTGGTATGGCTAGGCATTCAGGAACCGGAGAACGCTTCAGACCAGCCCGGACTGGGAACCTGCGGGCAGTAGGTGGAAT
```

**Expected output:**

```
Rosalind_0808
60.919540%
```

---

## 📁 Directory Structure

```
rosalind-dna/
├── README.md                    # This file
├── 01_count_nucleotides.py      # DNA: Counting DNA Nucleotides
├── 02_reverse_complement.py     # REVC: Reverse Complement
├── 03_gc_content.py             # GC: Computing GC Content
└── test_all.py                  # Full test suite (all 3 problems)
```

---

## 🚀 Quick Start

```bash
cd philomath-ai/rosalind-dna

# Run any individual problem (shows demo output with worked examples)
python 01_count_nucleotides.py
python 02_reverse_complement.py
python 03_gc_content.py

# Run the full test suite
python test_all.py
```

No additional dependencies are required — all modules use Python's standard
library only.

---

## 🎯 Learning Objectives

By working through this module you will understand:

### DNA Fundamentals
- The four DNA nucleotide bases: A, C, G, T
- Watson-Crick base pairing rules (A↔T, C↔G)
- Antiparallel strand orientation and the reverse complement
- GC content as a measure of sequence composition and thermal stability
- FASTA format for storing labelled sequences

### Python Skills
- Using dictionaries to accumulate character counts
- Iterating over strings with `for` loops and `reversed()`
- Parsing structured text formats (FASTA)
- Using `max()` with a `key` function
- Writing reusable functions with clear docstrings

### Bioinformatics Concepts
- Why both DNA strands must be searched for genes and motifs
- How GC content relates to biological properties
- FASTA as the universal sequence interchange format
- Profile and consensus sequences (foundations for Session 3+)

---

## 🔗 Resources

| Resource | Link |
|----------|------|
| Rosalind platform | https://rosalind.info |
| DNA problem | https://rosalind.info/problems/dna/ |
| REVC problem | https://rosalind.info/problems/revc/ |
| GC problem | https://rosalind.info/problems/gc/ |
| Philomath mailing list | http://eepurl.com/iC9DSg |
| Philomath membership | https://philomath.memberful.com |

---

## 📖 How This Fits Into Philomath AI

This module covers **Sessions 1–2** of the Philomath series, providing the
essential DNA string-manipulation skills that underpin all later problems.
It complements the other modules in `philomath-ai`:

- **[Rosalind Genetics](../rosalind-genetics/)** — Mendelian inheritance,
  probability, consensus sequences, and GC-content random string models
- **[Genome Algorithms](../genome_algorithms/)** — DNA pattern matching,
  clump finding, GC-skew analysis, and motif finding
- **[Monte Carlo Simulation](../monte-carlo/)** — random number generation
  and probability simulation

Together these modules build from raw sequence manipulation up through
probability theory and algorithmic bioinformatics.
