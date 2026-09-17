"""
One-step ingestion of benchmark outputs from bench/runner.py.

For the final report, the preferred reproducible command is:
    python tools/run_final_experiment.py --runs 200 --outdir results/final_200

This helper remains available for manual runner-output text files and supports
the revised repeated-run format with mean_time, median_time, expanded, and runs.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from statistics import mean, median
from typing import Any, Dict, List, Tuple

from parse_results import HEADERS, parse_file

Row = Dict[str, Any]


def merge(rows: List[Row]) -> List[Row]:
    idx: Dict[Tuple[str, str, str], Row] = {}
    for row in rows:
        idx[(row["src"], row["dst"], row["algo"])] = row

    merged: List[Row] = []
    for src, dst in sorted({(s, d) for (s, d, _algo) in idx}):
        d_row = idx.get((src, dst, "DIJKSTRA"))
        a_row = idx.get((src, dst, "ASTAR"))
        if not d_row or not a_row:
            continue
        if d_row["status"] != "OK" or a_row["status"] != "OK":
            continue

        d_time = float(d_row["mean_time_ms"])
        a_time = float(a_row["mean_time_ms"])
        d_cost = float(d_row["cost_km"])
        a_cost = float(a_row["cost_km"])
        cost_diff = abs(a_cost - d_cost)
        d_exp = int(d_row["expanded_nodes"] or 0)
        a_exp = int(a_row["expanded_nodes"] or 0)

        merged.append({
            "src": src,
            "dst": dst,
            "runs": int(d_row["runs"]),
            "dijkstra_mean_time_ms": d_time,
            "astar_mean_time_ms": a_time,
            "dijkstra_cost_km": d_cost,
            "astar_cost_km": a_cost,
            "cost_equal": cost_diff <= 1e-6,
            "cost_diff_km": cost_diff,
            "dijkstra_hops": int(d_row["hops"]),
            "astar_hops": int(a_row["hops"]),
            "dijkstra_expanded_nodes": d_exp,
            "astar_expanded_nodes": a_exp,
            "expanded_nodes_saved_by_astar": d_exp - a_exp,
            "speedup_mean_d_over_a": d_time / a_time if a_time > 0 else float("inf"),
            "mean_time_saved_ms": d_time - a_time,
        })
    return merged


def summarize(rows: List[Row]) -> Row:
    if not rows:
        return {"count_pairs": 0}
    return {
        "count_pairs": len(rows),
        "runs_per_pair_per_algorithm": int(rows[0]["runs"]),
        "pct_cost_equal": 100.0 * sum(1 for r in rows if r["cost_equal"]) / len(rows),
        "median_speedup_mean_time": median([r["speedup_mean_d_over_a"] for r in rows]),
        "mean_speedup_mean_time": mean([r["speedup_mean_d_over_a"] for r in rows]),
        "median_time_saved_ms": median([r["mean_time_saved_ms"] for r in rows]),
        "mean_time_saved_ms": mean([r["mean_time_saved_ms"] for r in rows]),
        "pct_pairs_astar_faster_mean_time": 100.0 * sum(1 for r in rows if r["mean_time_saved_ms"] > 0) / len(rows),
        "mean_dijkstra_expanded_nodes": mean([r["dijkstra_expanded_nodes"] for r in rows]),
        "mean_astar_expanded_nodes": mean([r["astar_expanded_nodes"] for r in rows]),
        "pct_pairs_astar_fewer_expansions": 100.0 * sum(1 for r in rows if r["expanded_nodes_saved_by_astar"] > 0) / len(rows),
    }


def write_csv(path: Path, rows: List[Row], headers: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if headers is None:
        headers = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", help="One or more runner output text files to parse.")
    parser.add_argument("--merged", required=True, help="Merged per-OD CSV output path.")
    parser.add_argument("--summary", required=True, help="Summary CSV output path.")
    parser.add_argument("--all", help="Optional: write full parsed rows to this CSV.")
    args = parser.parse_args()

    rows: List[Row] = []
    for inp in args.inputs:
        rows.extend(parse_file(Path(inp)))
    rows.sort(key=lambda r: (r["src"], r["dst"], r["algo"]))

    if args.all:
        write_csv(Path(args.all), rows, headers=HEADERS)
    merged = merge(rows)
    write_csv(Path(args.merged), merged)
    write_csv(Path(args.summary), [summarize(merged)])
    print(f"Wrote {len(merged)} merged rows to {args.merged}")
    print(f"Wrote summary to {args.summary}")


if __name__ == "__main__":
    main()
