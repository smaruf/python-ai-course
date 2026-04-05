# Rosalind Genetics & Probability — Episode 4

> **Part of [Philomath AI](../README.md)** — a comprehensive learning project from
> Phillip Compeau's "Programming for Lovers in Python" course.  
> See also: [Genome Algorithms](../genome_algorithms/) | [Monte Carlo Simulation](../monte-carlo/)

This module implements five genetics and probability problems from the
[Rosalind](https://rosalind.info) bioinformatics learning platform, solved
live in **Episode 4** of the Philomath problem-solving series hosted by
[Phillip Compeau](https://compeau.cbd.cmu.edu/) (Carnegie Mellon University,
Rosalind co-founder).

> 🎥 **Episode 4 stream** covered problems IPRB, IEV, LIA, PROB, and CONS —
> each combining classical genetics theory with practical Python programming.

---

## 📚 Problems Covered

| # | Problem | Rosalind ID | Topic |
|---|---------|-------------|-------|
| 1 | [Mendel's First Law](#1-iprb--mendels-first-law) | [IPRB](https://rosalind.info/problems/iprb/) | Mendelian genetics, probability |
| 2 | [Calculating Expected Offspring](#2-iev--calculating-expected-offspring) | [IEV](https://rosalind.info/problems/iev/) | Expected value, linearity |
| 3 | [Independent Alleles](#3-lia--independent-alleles) | [LIA](https://rosalind.info/problems/lia/) | Independent assortment, binomial distribution |
| 4 | [Introduction to Random Strings](#4-prob--introduction-to-random-strings) | [PROB](https://rosalind.info/problems/prob/) | GC-content, log-probabilities |
| 5 | [Consensus and Profile](#5-cons--consensus-and-profile) | [CONS](https://rosalind.info/problems/cons/) | Profile matrix, sequence conservation |

---

## 🧬 Problem Explanations

### 1. IPRB — Mendel's First Law

**Concept:** Gregor Mendel's First Law (Law of Segregation) states that during
reproduction, each parent passes exactly one randomly chosen allele to the
offspring.  A diploid organism carries two alleles:

| Genotype | Name | Phenotype |
|----------|------|-----------|
| `AA` | Homozygous dominant | Dominant |
| `Aa` | Heterozygous | Dominant |
| `aa` | Homozygous recessive | Recessive |

**Problem:** Given a population with `k` AA, `m` Aa, and `n` aa organisms,
find the probability that two randomly selected organisms produce a
**dominant-phenotype** offspring.

**Key insight — complement rule:**

```
P(dominant offspring) = 1 − P(offspring is aa)
```

Only four crosses can possibly produce an `aa` offspring:

| Cross | P(aa offspring) |
|-------|-----------------|
| Aa × Aa | 1/4 |
| Aa × aa | 1/2 |
| aa × Aa | 1/2 |
| aa × aa | 1 |

Because we sample **without replacement**, we count ordered pairs:
`P(cross type) = n₁ × n₂ / (total × (total − 1))`

**Sample:** k=2, m=2, n=2 → **P ≈ 0.78333**

---

### 2. IEV — Calculating Expected Offspring

**Concept:** The **expected value** of a random variable X with discrete
outcomes is:

```
E[X] = Σ  x · P(X = x)
```

**Linearity of expectation** is the key insight: the expected total is the
sum of the expected contributions from each couple type, regardless of
dependencies.

**Problem:** Given 6 integers representing the number of couples of each
Mendelian cross type, compute the expected number of **dominant-phenotype**
offspring (2 offspring per couple).

The six cross types and their dominant-phenotype probabilities:

| Cross | P(dominant offspring) |
|-------|----------------------|
| AA × AA | 1.00 |
| AA × Aa | 1.00 |
| AA × aa | 1.00 |
| Aa × Aa | 0.75 |
| Aa × aa | 0.50 |
| aa × aa | 0.00 |

**Formula:**
```
E = Σᵢ  cᵢ × 2 × P(dominantᵢ)
```

**Sample:** (1, 0, 0, 1, 0, 1) → **Expected = 3.5**

---

### 3. LIA — Independent Alleles

**Concept:** Mendel's Second Law (Law of Independent Assortment) states that
genes on different chromosomes assort independently.  For two traits:

```
P(Aa Bb offspring from Aa Bb × Aa Bb) = P(Aa) × P(Bb) = 1/2 × 1/2 = 1/4
```

This probability of 1/4 holds in **every generation** when each individual
always mates with an Aa Bb partner.

**Problem:** Starting from two Aa Bb parents, after `k` generations of
always mating with Aa Bb, what is the probability that at least `n` of the
`2^k` organisms in generation `k` are Aa Bb?

**Model:**
```
X ~ Binomial(N = 2^k, p = 1/4)

P(X ≥ n) = 1 − P(X < n) = 1 − Σᵢ₌₀ⁿ⁻¹  C(N, i) · (1/4)^i · (3/4)^(N−i)
```

The complement avoids summing a potentially long tail.

**Sample:** k=2, n=1 → **P ≈ 0.684**

---

### 4. PROB — Introduction to Random Strings

**Concept:** Under a random DNA model parameterised by GC-content `x`:

```
P(G) = P(C) = x / 2
P(A) = P(T) = (1 − x) / 2
```

The probability of observing a specific string `s` of length `n` is the
product of per-nucleotide probabilities.  For even moderate `n`, this
product underflows floating-point representation.  We work in
**log-probability space** instead:

```
log₁₀ P(s | x) = Σᵢ  log₁₀ P(sᵢ | x)      ← sum, not product
```

**Problem:** Given a DNA string and a list of GC-content values, return the
log₁₀ probability of generating that string at each GC-content.

**Why log-space?**
A string of length 100 at GC = 0.5 has probability ≈ (0.25)^100 ≈ 10⁻⁶⁰ —
too small for standard floating-point.  Log-space converts this to −60,
which is perfectly representable.

**Sample:** `ACGATACAA` at GC = 0.129 → **log₁₀ P ≈ −5.737**

---

### 5. CONS — Consensus and Profile

**Concept:** A **profile matrix** summarises a set of aligned DNA strings by
counting nucleotides at each position:

```
         pos 1  pos 2  pos 3  …
    A  [  5      1      0    …  ]
    C  [  0      0      1    …  ]
    G  [  1      1      6    …  ]
    T  [  1      5      0    …  ]
```

The **consensus sequence** is formed by selecting the most frequent
nucleotide at each position.  Highly conserved positions (high count for
one nucleotide) are often biologically significant — they may be part of a
binding motif or structurally critical site.

**Problem:** Given a collection of DNA strings (FASTA format, equal length),
output the consensus sequence and profile matrix.

**Algorithm:**
1. Parse FASTA → list of sequences
2. Increment `profile[nucleotide][position]` for each character
3. At each position, pick `argmax` over A, C, G, T

**Sample (7 × 8 strings):**
```
Consensus: ATGCAACT
A: 5 1 0 0 5 5 0 0
C: 0 0 1 4 2 0 6 1
G: 1 1 6 3 0 1 0 0
T: 1 5 0 0 0 1 1 6
```

---

## 📁 Directory Structure

```
rosalind-genetics/
├── README.md                         # This file
├── 01_iprb_mendels_first_law.py     # IPRB: Mendel's First Law
├── 02_iev_expected_offspring.py      # IEV: Calculating Expected Offspring
├── 03_lia_independent_alleles.py     # LIA: Independent Alleles
├── 04_prob_random_strings.py         # PROB: Introduction to Random Strings
├── 05_cons_consensus_profile.py      # CONS: Consensus and Profile
└── test_all.py                       # Full test suite (all 5 problems)
```

---

## 🚀 Quick Start

```bash
cd philomath-ai/rosalind-genetics

# Run any individual problem (shows demo output with worked examples)
python 01_iprb_mendels_first_law.py
python 02_iev_expected_offspring.py
python 03_lia_independent_alleles.py
python 04_prob_random_strings.py
python 05_cons_consensus_profile.py

# Run the full test suite
python test_all.py
```

No additional dependencies are required — all modules use Python's
standard library (`math` only).

---

## 🎯 Learning Objectives

By working through this module you will understand:

### Genetics
- Mendelian inheritance (dominance, recessiveness, segregation)
- Independent assortment of genes on different chromosomes
- Genotype vs phenotype distinction
- Punnett squares and their probabilistic interpretation

### Probability & Statistics
- Sampling without replacement and ordered pair counting
- The complement rule: P(A) = 1 − P(Aᶜ)
- Linearity of expectation
- Binomial distribution and CDF tail calculation
- Log-probability and numerical stability

### Bioinformatics
- GC-content as a model for random DNA sequences
- Profile matrices for summarising aligned sequences
- Consensus sequences and positional conservation
- FASTA format parsing

---

## 🔗 Resources

| Resource | Link |
|----------|------|
| Rosalind platform | https://rosalind.info |
| IPRB problem | https://rosalind.info/problems/iprb/ |
| IEV problem | https://rosalind.info/problems/iev/ |
| LIA problem | https://rosalind.info/problems/lia/ |
| PROB problem | https://rosalind.info/problems/prob/ |
| CONS problem | https://rosalind.info/problems/cons/ |
| Philomath mailing list | http://eepurl.com/iC9DSg |
| Philomath membership | https://philomath.memberful.com |

---

## 📖 How This Fits Into Philomath AI

This module is **Episode 4** of the Philomath live-coding series, covering
genetics and probability problems from Rosalind.  It complements the other
modules in `philomath-ai`:

- **[Genome Algorithms](../genome_algorithms/)** — DNA pattern matching, clump
  finding, GC-skew analysis, motif finding
- **[Monte Carlo Simulation](../monte-carlo/)** — random number generation,
  dice simulation, Craps probability
- **[Election Simulation](../election-simulation/)** — Electoral College
  forecasting using polling data

Together these modules cover a broad sweep of computational biology and
applied probability through hands-on problem solving.
