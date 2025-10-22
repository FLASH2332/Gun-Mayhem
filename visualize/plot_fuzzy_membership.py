"""
Plot fuzzy membership functions for Gun Mayhem AIs.

Features:
- Baseline FuzzyAI membership plots
- EvolvableFuzzyAI membership plots using a genome (default: evolved_genomes/best_genome.json)
- Overlay mode to compare baseline vs evolved on the same charts

Usage examples (run from anywhere):
  - python -u "visualize/plot_fuzzy_membership.py" --mode baseline --save fuzzy_baseline.png --show
  - python -u "visualize/plot_fuzzy_membership.py" --mode evolved --genome evolved_genomes/best_genome.json --save fuzzy_evolved.png
  - python -u "visualize/plot_fuzzy_membership.py" --mode both --genome evolved_genomes/best_genome.json --save fuzzy_overlay.png --show

Requirements:
- scikit-fuzzy, matplotlib
  pip install scikit-fuzzy matplotlib
"""
import os
import sys
import argparse
from typing import Dict, Tuple

# Ensure project root on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import numpy as np
import matplotlib.pyplot as plt

from fuzzy.fuzzy_ai import FuzzyAI, FUZZY_AVAILABLE
from fuzzy.evolvable_fuzzy_ai import EvolvableFuzzyAI
from ga.fuzzy_genome import FuzzyGenome


def _var_memberships(var) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
    """Return (x, curves) for a scikit-fuzzy control variable.
    curves is a dict: name -> membership array.
    """
    x = var.universe
    curves = {}
    for name, term in var.terms.items():
        try:
            curves[name] = term.mf
        except Exception:
            # Fallback: empty curve if something is off
            curves[name] = np.zeros_like(x, dtype=float)
    return x, curves


def _plot_one(ax, x, curves: Dict[str, np.ndarray], title: str, overlay=False):
    for name, y in curves.items():
        ax.plot(x, y, label=name)
    ax.set_title(title)
    ax.set_ylim([-0.05, 1.05])
    ax.grid(True, alpha=0.3)
    # For overlay mode we add legend outside once, otherwise per-axes is fine
    if not overlay:
        ax.legend(loc='upper right', fontsize=8)


def build_ai(mode: str, genome_path: str | None) -> Tuple[FuzzyAI | None, EvolvableFuzzyAI | None]:
    base_ai = None
    evo_ai = None
    if mode in ("baseline", "both"):
        base_ai = FuzzyAI()
    if mode in ("evolved", "both"):
        genome = None
        if genome_path and os.path.exists(genome_path):
            genome = FuzzyGenome.load(genome_path)
        else:
            genome = FuzzyGenome()  # fallback random if not found
        evo_ai = EvolvableFuzzyAI(genome)
    return base_ai, evo_ai


def main():
    parser = argparse.ArgumentParser(description="Plot fuzzy membership functions")
    parser.add_argument("--mode", choices=["baseline", "evolved", "both"], default="baseline",
                        help="Which membership set to plot")
    parser.add_argument("--genome", default=os.path.join(PROJECT_ROOT, "evolved_genomes", "best_genome.json"),
                        help="Path to genome JSON when mode is evolved/both")
    parser.add_argument("--save", default=os.path.join(PROJECT_ROOT, "visualize", "fuzzy_membership.png"),
                        help="Output image file path")
    parser.add_argument("--show", action="store_true", help="Display the figure in a window")

    args = parser.parse_args()

    if not FUZZY_AVAILABLE:
        print("ERROR: scikit-fuzzy not installed. Install with: pip install scikit-fuzzy matplotlib")
        sys.exit(1)

    base_ai, evo_ai = build_ai(args.mode, args.genome)

    # Collect variables to plot
    items = []
    if base_ai:
        items.append(("baseline", base_ai))
    if evo_ai:
        items.append(("evolved", evo_ai))

    # Prepare figure (6 panes)
    fig, axes = plt.subplots(3, 2, figsize=(12, 10))
    axes = axes.ravel()

    # Axes order and titles
    titles = [
        ("distance", "Distance"),
        ("health", "Health"),
        ("enemy_health", "Enemy Health"),
        ("height_diff", "Height Difference"),
        ("aggression", "Aggression (output)"),
        ("should_jump", "Should Jump (output)"),
    ]

    # Plot either single or overlay
    overlay = args.mode == "both"
    for idx, (attr, title) in enumerate(titles):
        ax = axes[idx]
        if overlay:
            # overlay baseline and evolved with different styles
            if base_ai:
                x, curves = _var_memberships(getattr(base_ai, attr))
                for name, y in curves.items():
                    ax.plot(x, y, label=f"baseline:{name}")
            if evo_ai:
                x2, curves2 = _var_memberships(getattr(evo_ai, attr))
                # dashed lines for evolved
                for name, y in curves2.items():
                    ax.plot(x2, y, linestyle='--', label=f"evolved:{name}")
            ax.set_title(title)
            ax.set_ylim([-0.05, 1.05])
            ax.grid(True, alpha=0.3)
        else:
            # single
            ai = base_ai if base_ai else evo_ai
            x, curves = _var_memberships(getattr(ai, attr))
            _plot_one(ax, x, curves, title, overlay=False)

    # Put a single legend outside if overlay
    if overlay:
        handles, labels = [], []
        for ax in axes:
            h, l = ax.get_legend_handles_labels()
            handles += h
            labels += l
        if handles:
            fig.legend(handles, labels, loc='upper center', ncol=3, fontsize=8, frameon=True)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.suptitle("Fuzzy Membership Functions" + (" (Overlay)" if overlay else ""))

    # Save and/or show
    out_dir = os.path.dirname(args.save)
    os.makedirs(out_dir, exist_ok=True)
    fig.savefig(args.save, dpi=150)
    print(f"Saved plot to: {args.save}")

    if args.show:
        try:
            plt.show()
        except Exception:
            # headless fallback
            pass


if __name__ == "__main__":
    main()
