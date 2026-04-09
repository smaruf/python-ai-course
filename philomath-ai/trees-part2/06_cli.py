"""
CLI: Command-Line Interface for Trees Part 2
============================================

Chapter 5 of "Programming for Lovers in Python" — Trees Part 2
by Phillip Compeau (Carnegie Mellon University).

Usage
-----
    python 06_cli.py recursion
    python 06_cli.py tree
    python 06_cli.py upgma --dataset great_apes
    python 06_cli.py upgma --dataset hemoglobin
    python 06_cli.py upgma --dataset hiv_subtypes
    python 06_cli.py upgma --dataset sars_cov2
    python 06_cli.py upgma --dataset mtdna_haplogroups
    python 06_cli.py upgma --file mydata.csv
    python 06_cli.py newick --dataset great_apes
    python 06_cli.py all

Learning Objectives
-------------------
- Practice building a real CLI with Python's argparse module
- Use sub-commands (subparsers) for different operation modes
- Integrate multiple modules through a single entry point
"""

import argparse
import importlib.util
import os
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))


def _load(filename: str):
    """Load a sibling module by filename."""
    path = os.path.join(_DIR, filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ─────────────────────────────────────────────────────────────────────────────
# Command handlers
# ─────────────────────────────────────────────────────────────────────────────

def cmd_recursion(args) -> None:
    """Demo factorial and Fibonacci with timing comparison."""
    rec = _load("01_recursion.py")

    print("=" * 70)
    print("RECURSION DEMO")
    print("=" * 70)

    print("\n── Factorial ──")
    for i in [0, 1, 5, 10, 15, 20]:
        print(f"  {i}! = {rec.factorial(i)}")

    print("\n── Fibonacci (first 20) ──")
    seq = [rec.fibonacci_iterative(k) for k in range(20)]
    print("  " + ", ".join(map(str, seq)))

    rec.compare_fibonacci_performance(max_n_naive=35, max_n_fast=55)


def cmd_tree(args) -> None:
    """Build and display a sample tree."""
    tn_mod = _load("02_tree_node.py")

    print("=" * 70)
    print("SAMPLE TREE DEMO")
    print("=" * 70)

    root = tn_mod.build_sample_tree()
    print("\nASCII tree:")
    print(root)
    print(f"\nTotal leaves: {root.count_leaves()}")
    print(f"Tree height:  {root.height():.4f}")


def cmd_upgma(args) -> None:
    """Run UPGMA on a dataset or CSV file."""
    pipeline = _load("05_pipeline.py")

    if args.file:
        # Load from CSV
        if not os.path.exists(args.file):
            print(f"Error: file not found: {args.file}")
            sys.exit(1)
        data = pipeline.load_csv(args.file)
        pipeline.run_pipeline(
            distance_matrix=data["matrix"],
            labels=data["labels"],
            dataset_name=os.path.basename(args.file),
        )
    else:
        dataset_name = args.dataset or "great_apes"
        if dataset_name not in pipeline.ALL_DATASETS:
            print(f"Unknown dataset '{dataset_name}'. "
                  f"Available: {', '.join(pipeline.ALL_DATASETS)}")
            sys.exit(1)
        ds = pipeline.ALL_DATASETS[dataset_name]
        pipeline.run_pipeline(
            distance_matrix=ds["matrix"],
            labels=ds["labels"],
            dataset_name=dataset_name,
            description=ds.get("description", ""),
        )


def cmd_newick(args) -> None:
    """Output Newick format for a dataset."""
    pipeline   = _load("05_pipeline.py")
    newick_mod = _load("04_newick.py")
    upgma_mod  = _load("03_upgma.py")

    dataset_name = args.dataset or "great_apes"
    if dataset_name not in pipeline.ALL_DATASETS:
        print(f"Unknown dataset '{dataset_name}'. "
              f"Available: {', '.join(pipeline.ALL_DATASETS)}")
        sys.exit(1)

    ds   = pipeline.ALL_DATASETS[dataset_name]
    root = upgma_mod.upgma(ds["matrix"], ds["labels"])
    nwk  = newick_mod.to_newick(root)

    print("=" * 70)
    print(f"NEWICK: {dataset_name.upper()}")
    print("=" * 70)
    print(f"\n{nwk}\n")


def cmd_all(args) -> None:
    """Run all demos in sequence."""
    cmd_recursion(args)
    cmd_tree(args)
    pipeline = _load("05_pipeline.py")
    for name, ds in pipeline.ALL_DATASETS.items():
        pipeline.run_pipeline(
            distance_matrix=ds["matrix"],
            labels=ds["labels"],
            dataset_name=name,
            description=ds.get("description", ""),
        )


# ─────────────────────────────────────────────────────────────────────────────
# Argument parser
# ─────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="06_cli.py",
        description=(
            "Trees Part 2 — UPGMA phylogenetics CLI\n"
            "Chapter 5 of Programming for Lovers in Python"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    subparsers.required = True

    # recursion
    subparsers.add_parser("recursion", help="Demo factorial and Fibonacci")

    # tree
    subparsers.add_parser("tree", help="Build and display a sample tree")

    # upgma
    upgma_p = subparsers.add_parser("upgma", help="Run UPGMA on a dataset")
    upgma_p.add_argument(
        "--dataset", "-d",
        default="great_apes",
        metavar="NAME",
        help="Dataset name: great_apes, hemoglobin, hiv_subtypes, sars_cov2, "
             "mtdna_haplogroups (default: great_apes)",
    )
    upgma_p.add_argument(
        "--file", "-f",
        metavar="CSV",
        help="Path to a CSV distance matrix file",
    )

    # newick
    newick_p = subparsers.add_parser("newick", help="Output Newick format")
    newick_p.add_argument(
        "--dataset", "-d",
        default="great_apes",
        metavar="NAME",
        help="Dataset name (default: great_apes)",
    )

    # all
    subparsers.add_parser("all", help="Run all demos")

    return parser


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = build_parser()
    args   = parser.parse_args()

    handlers = {
        "recursion": cmd_recursion,
        "tree":      cmd_tree,
        "upgma":     cmd_upgma,
        "newick":    cmd_newick,
        "all":       cmd_all,
    }
    handlers[args.command](args)
