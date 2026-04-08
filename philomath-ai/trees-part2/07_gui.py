"""
GUI: Tkinter Interface for Trees Part 2
========================================

Chapter 5 of "Programming for Lovers in Python" — Trees Part 2
by Phillip Compeau (Carnegie Mellon University).

Features
--------
- Tab 1 (UPGMA): Dataset dropdown, Run button, distance matrix display,
  Newick output, and ASCII tree — all in a scrollable text widget.
- Tab 2 (Recursion): Input n, buttons for Factorial/Fibonacci (all three
  variants), timing display.

No external dependencies — tkinter is part of Python's standard library.

Run:
    python 07_gui.py
"""

import importlib.util
import os
import sys
import time
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox

_DIR = os.path.dirname(os.path.abspath(__file__))


def _load(filename: str):
    """Load a sibling module by filename."""
    path = os.path.join(_DIR, filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ─────────────────────────────────────────────────────────────────────────────
# Main Application
# ─────────────────────────────────────────────────────────────────────────────

class TreesApp(tk.Tk):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.title("Trees Part 2 — UPGMA Phylogenetics")
        self.geometry("900x680")
        self.resizable(True, True)
        self._build_ui()

    # ── UI construction ────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        self._build_upgma_tab(notebook)
        self._build_recursion_tab(notebook)

    # ── Tab 1: UPGMA ──────────────────────────────────────────────────────────

    def _build_upgma_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="UPGMA Phylogenetics")

        # ── Controls (top bar) ────
        ctrl = ttk.LabelFrame(frame, text="Controls", padding=6)
        ctrl.pack(fill=tk.X, padx=6, pady=(6, 2))

        ttk.Label(ctrl, text="Dataset:").grid(row=0, column=0, sticky=tk.W, padx=4)
        self._dataset_var = tk.StringVar(value="great_apes")
        datasets = ["great_apes", "hemoglobin", "hiv_subtypes",
                    "sars_cov2", "mtdna_haplogroups"]
        ds_combo = ttk.Combobox(
            ctrl, textvariable=self._dataset_var,
            values=datasets, state="readonly", width=22,
        )
        ds_combo.grid(row=0, column=1, padx=4)

        ttk.Button(ctrl, text="Run UPGMA",
                   command=self._run_upgma).grid(row=0, column=2, padx=8)
        ttk.Button(ctrl, text="Load CSV…",
                   command=self._load_csv).grid(row=0, column=3, padx=2)

        # ── Output area ──────────
        out_frame = ttk.LabelFrame(frame, text="Output", padding=4)
        out_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        self._upgma_text = scrolledtext.ScrolledText(
            out_frame, wrap=tk.NONE,
            font=("Courier New", 10), state=tk.DISABLED,
        )
        self._upgma_text.pack(fill=tk.BOTH, expand=True)

        # Horizontal scrollbar
        hbar = ttk.Scrollbar(out_frame, orient=tk.HORIZONTAL,
                              command=self._upgma_text.xview)
        self._upgma_text.configure(xscrollcommand=hbar.set)
        hbar.pack(fill=tk.X)

    # ── Tab 2: Recursion ──────────────────────────────────────────────────────

    def _build_recursion_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Recursion Demo")

        ctrl = ttk.LabelFrame(frame, text="Controls", padding=8)
        ctrl.pack(fill=tk.X, padx=6, pady=(6, 2))

        ttk.Label(ctrl, text="n =").grid(row=0, column=0, sticky=tk.W, padx=4)
        self._n_var = tk.StringVar(value="10")
        ttk.Entry(ctrl, textvariable=self._n_var, width=8).grid(
            row=0, column=1, padx=4)

        ttk.Button(ctrl, text="Factorial",
                   command=self._calc_factorial).grid(row=0, column=2, padx=6)
        ttk.Button(ctrl, text="Fib (naive)",
                   command=self._calc_fib_naive).grid(row=0, column=3, padx=2)
        ttk.Button(ctrl, text="Fib (memo)",
                   command=self._calc_fib_memo).grid(row=0, column=4, padx=2)
        ttk.Button(ctrl, text="Fib (iter)",
                   command=self._calc_fib_iter).grid(row=0, column=5, padx=2)
        ttk.Button(ctrl, text="Compare all",
                   command=self._compare_all).grid(row=0, column=6, padx=6)

        out_frame = ttk.LabelFrame(frame, text="Output", padding=4)
        out_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        self._rec_text = scrolledtext.ScrolledText(
            out_frame, wrap=tk.NONE,
            font=("Courier New", 10), state=tk.DISABLED,
        )
        self._rec_text.pack(fill=tk.BOTH, expand=True)

    # ── UPGMA callbacks ────────────────────────────────────────────────────────

    def _run_upgma(self) -> None:
        pipeline   = _load("05_pipeline.py")
        newick_mod = _load("04_newick.py")
        upgma_mod  = _load("03_upgma.py")

        name = self._dataset_var.get()
        if name not in pipeline.ALL_DATASETS:
            messagebox.showerror("Error", f"Unknown dataset: {name}")
            return

        ds = pipeline.ALL_DATASETS[name]
        self._show_upgma_result(ds["matrix"], ds["labels"], name,
                                ds.get("description", ""),
                                upgma_mod, newick_mod)

    def _load_csv(self) -> None:
        pipeline = _load("05_pipeline.py")
        filepath = filedialog.askopenfilename(
            title="Open distance matrix CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not filepath:
            return
        try:
            data = pipeline.load_csv(filepath)
        except Exception as exc:
            messagebox.showerror("CSV Load Error", str(exc))
            return

        upgma_mod  = _load("03_upgma.py")
        newick_mod = _load("04_newick.py")
        self._show_upgma_result(
            data["matrix"], data["labels"],
            os.path.basename(filepath), "",
            upgma_mod, newick_mod,
        )

    def _show_upgma_result(self, matrix, labels, name, description,
                            upgma_mod, newick_mod) -> None:
        import io
        buf = io.StringIO()

        # Header
        buf.write("=" * 70 + "\n")
        buf.write(f"DATASET: {name.upper()}\n")
        buf.write("=" * 70 + "\n")
        if description:
            buf.write(f"\n{description}\n")

        # Distance matrix
        buf.write("\nDistance Matrix:\n")
        col_w = max(len(lb) for lb in labels) + 2
        buf.write(" " * col_w + "".join(f"{lb:>{col_w}}" for lb in labels) + "\n")
        for i, row in enumerate(matrix):
            cells = "".join(f"{v:>{col_w}.4f}" for v in row)
            buf.write(f"{labels[i]:<{col_w}}{cells}\n")

        # Run UPGMA
        try:
            root = upgma_mod.upgma(matrix, labels)
        except Exception as exc:
            messagebox.showerror("UPGMA Error", str(exc))
            return

        newick = newick_mod.to_newick(root)

        buf.write(f"\nASCII Tree:\n{root}\n")
        buf.write(f"\nNewick:\n{newick}\n")
        buf.write(f"\nLeaves: {root.count_leaves()}\n")

        self._set_text(self._upgma_text, buf.getvalue())

    # ── Recursion callbacks ────────────────────────────────────────────────────

    def _get_n(self) -> int | None:
        try:
            n = int(self._n_var.get())
            if n < 0:
                raise ValueError("n must be non-negative")
            return n
        except ValueError as exc:
            messagebox.showerror("Input Error", str(exc))
            return None

    def _calc_factorial(self) -> None:
        n = self._get_n()
        if n is None:
            return
        rec = _load("01_recursion.py")
        try:
            t, result = rec.time_call(rec.factorial, n)
            self._append_rec(f"factorial({n}) = {result}  [{t*1000:.4f} ms]\n")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _calc_fib_naive(self) -> None:
        n = self._get_n()
        if n is None:
            return
        if n > 40:
            messagebox.showwarning(
                "Large n",
                f"n={n} is large for naive Fibonacci (O(2^n)).\n"
                "Consider using n ≤ 35 to avoid very long wait times."
            )
        rec = _load("01_recursion.py")
        try:
            t, result = rec.time_call(rec.fibonacci_naive, n)
            self._append_rec(f"fibonacci_naive({n}) = {result}  [{t*1000:.4f} ms]\n")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _calc_fib_memo(self) -> None:
        n = self._get_n()
        if n is None:
            return
        rec = _load("01_recursion.py")
        t, result = rec.time_call(rec.fibonacci_memo, n)
        self._append_rec(f"fibonacci_memo({n}) = {result}  [{t*1000:.6f} ms]\n")

    def _calc_fib_iter(self) -> None:
        n = self._get_n()
        if n is None:
            return
        rec = _load("01_recursion.py")
        t, result = rec.time_call(rec.fibonacci_iterative, n)
        self._append_rec(f"fibonacci_iter({n}) = {result}  [{t*1000:.6f} ms]\n")

    def _compare_all(self) -> None:
        n = self._get_n()
        if n is None:
            return
        rec = _load("01_recursion.py")
        import io, sys

        cap = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = cap
        rec.compare_fibonacci_performance(
            max_n_naive=min(n, 35),
            max_n_fast=max(n, 50),
        )
        sys.stdout = old_stdout
        self._append_rec(cap.getvalue())

    # ── Text widget helpers ────────────────────────────────────────────────────

    @staticmethod
    def _set_text(widget: scrolledtext.ScrolledText, text: str) -> None:
        widget.configure(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, text)
        widget.configure(state=tk.DISABLED)

    def _append_rec(self, text: str) -> None:
        self._rec_text.configure(state=tk.NORMAL)
        self._rec_text.insert(tk.END, text)
        self._rec_text.configure(state=tk.DISABLED)
        self._rec_text.see(tk.END)


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = TreesApp()
    app.mainloop()
