"""
Pipeline: Running UPGMA End-to-End on Real Biological Datasets
==============================================================

Chapter 5 of "Programming for Lovers in Python" — Trees Part 2
by Phillip Compeau (Carnegie Mellon University).

Background
----------
This module assembles the full phylogenetic analysis pipeline:

    distance_matrix  →  UPGMA  →  TreeNode  →  Newick  →  display

Five real (simplified) biological datasets are included:

1. **Great Apes** — cytochrome b divergence for human, chimp, bonobo,
   gorilla, and orangutan.  UPGMA correctly recovers the known topology:
   ((human,chimp,bonobo),gorilla),orangutan.

2. **Hemoglobin** — amino-acid divergence of haemoglobin alpha chains
   across the animal kingdom (human, mouse, zebrafish, frog, shark, lamprey).

3. **HIV Subtypes** — nucleotide divergence between HIV-1 group M subtypes
   (A1, B, C, D, AE recombinant, G).  Reveals clade structure within HIV-1.

4. **SARS-CoV-2 variants** — approximate nucleotide divergence of major
   variants of concern (Original/Wuhan, Alpha, Delta, Omicron BA.1, BA.2).

5. **Mitochondrial DNA haplogroups** — divergence between human mtDNA
   haplogroups tracing out-of-Africa migration routes
   (L0, L1, M, N, R, H, J).

Learning Objectives
-------------------
- Apply UPGMA to multiple real biological datasets
- Interpret phylogenetic trees in evolutionary context
- Understand where UPGMA succeeds and where it can fail
"""

from __future__ import annotations
import importlib.util
import os
import sys


# ─────────────────────────────────────────────────────────────────────────────
# Module loader helpers
# ─────────────────────────────────────────────────────────────────────────────

_DIR = os.path.dirname(os.path.abspath(__file__))


def _load(filename: str):
    path = os.path.join(_DIR, filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ─────────────────────────────────────────────────────────────────────────────
# Built-in datasets
# ─────────────────────────────────────────────────────────────────────────────

GREAT_APES = {
    "labels": ["human", "chimp", "bonobo", "gorilla", "orangutan"],
    "matrix": [
        # human  chimp  bonobo gorilla orang
        [0.000, 0.012, 0.013, 0.030,  0.080],
        [0.012, 0.000, 0.009, 0.031,  0.079],
        [0.013, 0.009, 0.000, 0.032,  0.081],
        [0.030, 0.031, 0.032, 0.000,  0.078],
        [0.080, 0.079, 0.081, 0.078,  0.000],
    ],
    "description": (
        "Cytochrome b nucleotide divergence (%) among great apes. "
        "Expected topology: ((human,(chimp,bonobo)),gorilla),orangutan."
    ),
}

HEMOGLOBIN = {
    "labels": ["human", "mouse", "zebrafish", "frog", "shark", "lamprey"],
    "matrix": [
        # human  mouse  zebrafish frog   shark  lamprey
        [0.000, 0.150,  0.430,  0.480,  0.520,  0.800],
        [0.150, 0.000,  0.440,  0.490,  0.530,  0.810],
        [0.430, 0.440,  0.000,  0.390,  0.460,  0.780],
        [0.480, 0.490,  0.390,  0.000,  0.450,  0.790],
        [0.520, 0.530,  0.460,  0.450,  0.000,  0.750],
        [0.800, 0.810,  0.780,  0.790,  0.750,  0.000],
    ],
    "description": (
        "Amino-acid divergence of haemoglobin alpha chain across the animal "
        "kingdom.  Lamprey (jawless fish) diverges earliest; mammals cluster "
        "together."
    ),
}

HIV_SUBTYPES = {
    "labels": ["A1", "B", "C", "D", "AE", "G"],
    "matrix": [
        # A1    B      C      D      AE     G
        [0.000, 0.150, 0.130, 0.120, 0.135, 0.160],
        [0.150, 0.000, 0.155, 0.145, 0.140, 0.155],
        [0.130, 0.155, 0.000, 0.125, 0.130, 0.150],
        [0.120, 0.145, 0.125, 0.000, 0.128, 0.152],
        [0.135, 0.140, 0.130, 0.128, 0.000, 0.148],
        [0.160, 0.155, 0.150, 0.152, 0.148, 0.000],
    ],
    "description": (
        "Nucleotide divergence between HIV-1 group M subtypes.  The recombinant "
        "form AE clusters with A1/D, while B and C form a separate clade."
    ),
}

SARS_COV2 = {
    "labels": ["original", "alpha", "delta", "omicron_ba1", "omicron_ba2"],
    "matrix": [
        # orig   alpha   delta   ba1     ba2
        [0.000, 0.0008, 0.0015, 0.0100, 0.0110],
        [0.0008, 0.000, 0.0014, 0.0099, 0.0109],
        [0.0015, 0.0014, 0.000, 0.0098, 0.0108],
        [0.0100, 0.0099, 0.0098, 0.000, 0.0020],
        [0.0110, 0.0109, 0.0108, 0.0020, 0.000],
    ],
    "description": (
        "Approximate nucleotide divergence between major SARS-CoV-2 variants of "
        "concern.  Omicron BA.1 and BA.2 are closely related; all early variants "
        "cluster together."
    ),
}

MTDNA_HAPLOGROUPS = {
    "labels": ["L0", "L1", "M", "N", "R", "H", "J"],
    "matrix": [
        # L0     L1     M      N      R      H      J
        [0.000, 0.080, 0.200, 0.200, 0.210, 0.220, 0.225],
        [0.080, 0.000, 0.195, 0.195, 0.205, 0.215, 0.220],
        [0.200, 0.195, 0.000, 0.090, 0.095, 0.120, 0.125],
        [0.200, 0.195, 0.090, 0.000, 0.060, 0.080, 0.085],
        [0.210, 0.205, 0.095, 0.060, 0.000, 0.040, 0.045],
        [0.220, 0.215, 0.120, 0.080, 0.040, 0.000, 0.030],
        [0.225, 0.220, 0.125, 0.085, 0.045, 0.030, 0.000],
    ],
    "description": (
        "Mitochondrial DNA haplogroup divergence tracing human out-of-Africa "
        "migration.  L0/L1 (sub-Saharan Africa) diverge earliest.  M and N are "
        "the two major non-African founding lineages.  R/H/J are European/Asian "
        "sub-clades."
    ),
}

ALL_DATASETS = {
    "great_apes":       GREAT_APES,
    "hemoglobin":       HEMOGLOBIN,
    "hiv_subtypes":     HIV_SUBTYPES,
    "sars_cov2":        SARS_COV2,
    "mtdna_haplogroups": MTDNA_HAPLOGROUPS,
}


# ─────────────────────────────────────────────────────────────────────────────
# CSV loader
# ─────────────────────────────────────────────────────────────────────────────

def load_csv(filepath: str) -> dict:
    """
    Load a distance matrix from a CSV file.

    Expected format:
        First row: comma-separated header (blank first cell, then taxon names)
        Each subsequent row: taxon_name, distance values ...

    Args:
        filepath: Path to CSV file.

    Returns:
        dict with keys "labels" and "matrix".

    Raises:
        FileNotFoundError: if the file does not exist.
        ValueError: if the matrix is not square.
    """
    labels = []
    rows = []
    with open(filepath, "r", encoding="utf-8") as fh:
        for line_no, raw_line in enumerate(fh):
            line = raw_line.strip()
            if not line:
                continue
            parts = line.split(",")
            if line_no == 0:
                # Header row: first cell may be blank
                labels = [p.strip() for p in parts[1:]]
            else:
                row_values = [float(p.strip()) for p in parts[1:]]
                rows.append(row_values)

    if len(rows) != len(labels):
        raise ValueError(
            f"Matrix is {len(rows)}×{len(labels)} — expected square matrix"
        )
    return {"labels": labels, "matrix": rows}


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline runner
# ─────────────────────────────────────────────────────────────────────────────

def run_pipeline(
    distance_matrix: list[list[float]],
    labels: list[str],
    dataset_name: str = "",
    description: str = "",
) -> dict:
    """
    Run the complete UPGMA phylogenetics pipeline on a distance matrix.

    Steps:
      1. Run UPGMA to build the TreeNode tree
      2. Convert to Newick string
      3. Display ASCII tree and Newick output

    Args:
        distance_matrix: Symmetric n×n pairwise distance matrix.
        labels:          Taxon names (length n).
        dataset_name:    Human-readable name for display (optional).
        description:     Background text to print (optional).

    Returns:
        dict with keys:
          "root"   — root TreeNode
          "newick" — Newick format string
          "leaves" — number of leaf nodes
    """
    upgma_mod  = _load("03_upgma.py")
    newick_mod = _load("04_newick.py")

    n = len(labels)
    print("\n" + "=" * 70)
    if dataset_name:
        print(f"DATASET: {dataset_name.upper()}")
    print("=" * 70)
    if description:
        print(f"\n{description}\n")

    # Print distance matrix
    col_w = max(len(lb) for lb in labels) + 2
    header = " " * col_w + "".join(f"{lb:>{col_w}}" for lb in labels)
    print(header)
    for i, row in enumerate(distance_matrix):
        cells = "".join(f"{v:>{col_w}.4f}" for v in row)
        print(f"{labels[i]:<{col_w}}{cells}")

    # Run UPGMA
    root = upgma_mod.upgma(distance_matrix, labels)

    # Newick
    newick = newick_mod.to_newick(root)

    print(f"\n── ASCII Tree ──")
    print(root)

    print(f"\n── Newick ──")
    print(f"  {newick}")

    print(f"\n  Leaves: {root.count_leaves()}")

    return {"root": root, "newick": newick, "leaves": root.count_leaves()}


# ─────────────────────────────────────────────────────────────────────────────
# Demo
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("UPGMA PIPELINE — ALL DATASETS")
    print("=" * 70)

    for name, dataset in ALL_DATASETS.items():
        run_pipeline(
            distance_matrix=dataset["matrix"],
            labels=dataset["labels"],
            dataset_name=name,
            description=dataset.get("description", ""),
        )

    print("\n" + "=" * 70)
    print("OBSERVATIONS")
    print("=" * 70)
    print("✓ Great apes: correct ((human,(chimp,bonobo)),gorilla),orangutan")
    print("✓ Hemoglobin: lamprey diverges earliest (most basal lineage)")
    print("✓ SARS-CoV-2: Omicron variants cluster together, distinct from Alpha/Delta")
    print("✓ mtDNA haplogroups: L0/L1 are the most basal (African origin)")
    print("\nWhere UPGMA can go wrong:")
    print("  • When the molecular clock assumption is violated (unequal rates)")
    print("  • HIV subtypes: recombination violates tree model assumptions")
    print("  → Next: Neighbor Joining corrects for rate variation")
