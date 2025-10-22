"""
Summarize a tournament JSON into Markdown or CSV tables.
- Handles both new format (with p1_name/p2_name, winner_name, winner_side) and older format (reconstructs side mapping by match parity).

Usage:
  python -u visualize/summarize_tournament.py --file visualize/tournament_results/tournament_XXXXXXXX.json --format markdown --out visualize/tournament_results/summary.md

Outputs two sections/tables by default:
- Pair summary (wins/losses/draws, win rates)
- Per-match table with identities aligned

"""
import os
import sys
import json
import argparse
from typing import Any, Dict, List, Tuple

# Ensure project root on path for convenience (not strictly needed here)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def _md_row(cells: List[str]) -> str:
    return "| " + " | ".join(cells) + " |\n"


def _csv_row(cells: List[str]) -> str:
    # Simple CSV: quote if contains comma or quotes
    out = []
    for c in cells:
        if any(ch in c for ch in [',', '"', '\n', '\r']):
            c = '"' + c.replace('"', '""') + '"'
        out.append(c)
    return ",".join(out) + "\n"


def _bool(v: Any) -> bool:
    return bool(v)


def load_json(path: str) -> Dict[str, Any]:
    with open(path, 'r') as f:
        return json.load(f)


def identity_for_sides(pair_p1: str, pair_p2: str, match_idx: int, alternate_sides: bool) -> Tuple[str, str]:
    """Return (p1_name, p2_name) for this match, reconstructing if needed."""
    if not alternate_sides:
        return pair_p1, pair_p2
    # match numbers are 1-indexed in our JSON; even matches swapped
    if (match_idx % 2) == 1:
        return pair_p1, pair_p2
    else:
        return pair_p2, pair_p1


def summarize(file_path: str, out_fmt: str, out_file: str = None, include_per_match: bool = True) -> str:
    data = load_json(file_path)
    alternate_sides = data.get('alternate_sides', True)

    # Pair-level summary table (from JSON summaries if present)
    summary_rows = []
    for pair in data.get('pairs', []):
        p1 = pair.get('p1', '')
        p2 = pair.get('p2', '')
        s = pair.get('summary', {})
        total = (s.get('p1_wins', 0) + s.get('p2_wins', 0) + s.get('draws', 0)) or 1
        wr1 = f"{(100.0 * s.get('p1_wins', 0) / total):.1f}%"
        wr2 = f"{(100.0 * s.get('p2_wins', 0) / total):.1f}%"
        summary_rows.append([
            f"{p1} vs {p2}",
            str(data.get('matches_per_pair', '')),
            str(s.get('p1_wins', 0)),
            str(s.get('p2_wins', 0)),
            str(s.get('draws', 0)),
            wr1,
            wr2,
        ])

    # Per-match rows aligned by identity
    match_rows: List[List[str]] = []
    for pair in data.get('pairs', []):
        pair_name = pair.get('pair', '')
        p1 = pair.get('p1', '')
        p2 = pair.get('p2', '')
        for r in pair.get('results', []):
            m = r.get('match')
            stats = r.get('stats', {})
            # Prefer new fields when present
            p1_name = r.get('p1_name')
            p2_name = r.get('p2_name')
            winner_name = r.get('winner_name')
            winner_side = r.get('winner_side')
            # Backfill for older files
            if not p1_name or not p2_name:
                p1_name, p2_name = identity_for_sides(p1, p2, m, alternate_sides)
            if not winner_name:
                w = r.get('winner')
                if w == 'ai1':
                    # ai1 corresponds to pair.p1 (identity)
                    winner_name = pair.get('p1', '')
                elif w == 'ai2':
                    winner_name = pair.get('p2', '')
                else:
                    winner_name = 'draw'
            if not winner_side:
                # Rough side inference: if m is odd (and alternation), ai1 was p1; else p2
                if not alternate_sides:
                    # ai1 always p1 in non-alternate mode -> side aligns with identity winner
                    w = r.get('winner')
                    winner_side = 'p1' if w == 'ai1' else ('p2' if w == 'ai2' else 'none')
                else:
                    if (m % 2) == 1:
                        w = r.get('winner')
                        winner_side = 'p1' if w == 'ai1' else ('p2' if w == 'ai2' else 'none')
                    else:
                        w = r.get('winner')
                        winner_side = 'p1' if w == 'ai2' else ('p2' if w == 'ai1' else 'none')

            row = [
                pair_name,
                str(m),
                p1_name,
                p2_name,
                winner_name,
                winner_side or 'none',
                str(stats.get('frames', '')),
                str(stats.get('p1_lives', '')),
                str(stats.get('p2_lives', '')),
                str(stats.get('p1_health', '')),
                str(stats.get('p2_health', '')),
                str(stats.get('shots1', '')),
                str(stats.get('shots2', '')),
                f"{stats.get('avg_distance', '')}",
            ]
            match_rows.append(row)

    # Build output
    out_parts: List[str] = []
    if out_fmt == 'markdown':
        # Summary
        out_parts.append("## Pair summary\n\n")
        out_parts.append(_md_row(["Pair", "Matches", "P1 wins", "P2 wins", "Draws", "P1 win%", "P2 win%"]))
        out_parts.append(_md_row(["---", "---", "---", "---", "---", "---", "---"]))
        for row in summary_rows:
            out_parts.append(_md_row(row))
        # Per-match
        if match_rows:
            out_parts.append("\n## Per-match results (identity-aligned)\n\n")
            header = [
                "Pair", "Match", "P1 name", "P2 name", "Winner", "Winner side",
                "Frames", "P1 lives", "P2 lives", "P1 health", "P2 health", "Shots1", "Shots2", "Avg distance"
            ]
            out_parts.append(_md_row(header))
            out_parts.append(_md_row(["---"] * len(header)))
            for row in match_rows:
                out_parts.append(_md_row(row))
        result = "".join(out_parts)
    else:  # csv
        # Summary
        out_parts.append("Pair,Matches,P1 wins,P2 wins,Draws,P1 win%,P2 win%\n")
        for row in summary_rows:
            out_parts.append(_csv_row(row))
        # Per-match
        if match_rows:
            out_parts.append("\nPair,Match,P1 name,P2 name,Winner,Winner side,Frames,P1 lives,P2 lives,P1 health,P2 health,Shots1,Shots2,Avg distance\n")
            for row in match_rows:
                out_parts.append(_csv_row(row))
        result = "".join(out_parts)

    if out_file:
        os.makedirs(os.path.dirname(out_file), exist_ok=True)
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(result)
    return result


def main():
    p = argparse.ArgumentParser(description="Summarize tournament results into Markdown or CSV")
    p.add_argument('--file', required=True, help='Path to tournament_*.json')
    p.add_argument('--format', choices=['markdown', 'csv'], default='markdown')
    p.add_argument('--out', help='Write output to this file (otherwise print)')
    args = p.parse_args()

    text = summarize(args.file, args.format, args.out)
    if not args.out:
        # Print to console
        sys.stdout.write(text)


if __name__ == '__main__':
    main()
