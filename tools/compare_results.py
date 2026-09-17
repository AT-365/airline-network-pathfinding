"""
Compare Dijkstra vs A* results and compute speedups.

This helper is kept for manual/legacy workflows. The official final-results
script is tools/run_final_experiment.py. This script accepts either a legacy
`time_ms` column or the revised `mean_time_ms` column from tools/parse_results.py.

Input:
  A CSV produced by tools/parse_results.py with columns such as:
    algo, src, dst, mean_time_ms, cost_km, hops, status

Outputs:
  --out <merged.csv>     Wide per-OD table with both algos and speedup metrics.
  --summary <summary.csv> One-line summary of aggregates.

Usage:
  python tools/compare_results.py results_all.csv --out results_merged.csv --summary results_summary.csv
"""
from __future__ import annotations
import argparse
import csv
from pathlib import Path
from statistics import mean, median
from typing import Dict, Tuple, List

Row = Dict[str, str | float | int]

def read_rows(path: Path) -> List[Row]:
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        rows = []
        for row in r:
            rows.append({
                "algo": str(row["algo"]).upper(),
                "src": str(row["src"]).upper(),
                "dst": str(row["dst"]).upper(),
                "time_ms": float(row.get("time_ms") or row.get("mean_time_ms")),
                "cost_km": float(row["cost_km"]) if str(row["cost_km"]).lower() != "inf" else float("inf"),
                "hops": int(row["hops"]),
                "status": str(row["status"]).upper(),
            })
        return rows

def merge(rows: List[Row]) -> List[Row]:
    # Index by (src, dst, algo)
    idx: Dict[Tuple[str, str, str], Row] = {}
    for r in rows:
        key = (r["src"], r["dst"], r["algo"])
        idx[key] = r

    merged: List[Row] = []
    # Build rows only where both DIJKSTRA and ASTAR exist
    pairs = {(s, d) for (s, d, a) in idx.keys()}
    for s, d in sorted(pairs):
        di = idx.get((s, d, "DIJKSTRA"))
        as_ = idx.get((s, d, "ASTAR"))
        if not di or not as_:
            continue
        # Only consider OK statuses
        if di["status"] != "OK" or as_["status"] != "OK":
            continue
        cost_diff = abs(float(as_["cost_km"]) - float(di["cost_km"]))
        cost_equal = cost_diff <= 1e-6

        t_d = float(di["time_ms"])
        t_a = float(as_["time_ms"])
        if t_a <= 0.0:
            speedup = float("inf")
            pct_faster = 100.0
            delta_ms = t_d - t_a
        else:
            speedup = t_d / t_a
            pct_faster = (1.0 - (t_a / t_d)) * 100.0 if t_d > 0.0 else float("inf")
            delta_ms = t_d - t_a

        merged.append({
            "src": s, "dst": d,
            "dijkstra_time_ms": t_d, "astar_time_ms": t_a,
            "dijkstra_cost_km": float(di["cost_km"]), "astar_cost_km": float(as_["cost_km"]),
            "dijkstra_hops": int(di["hops"]), "astar_hops": int(as_["hops"]),
            "cost_equal": cost_equal, "cost_diff_km": cost_diff,
            "speedup_d_over_a": speedup,          # >1 means A* is faster
            "time_saved_ms": delta_ms,            # positive means A* faster
            "pct_time_reduction": pct_faster,     # percent reduction from Dijkstra to A*
        })
    return merged

def write_csv(path: Path, rows: List[Row]) -> None:
    if not rows:
        # Write headers anyway for consistency
        headers = [
            "src","dst",
            "dijkstra_time_ms","astar_time_ms",
            "dijkstra_cost_km","astar_cost_km",
            "dijkstra_hops","astar_hops",
            "cost_equal","cost_diff_km",
            "speedup_d_over_a","time_saved_ms","pct_time_reduction",
        ]
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=headers)
            w.writeheader()
        return

    headers = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(rows)

def summarize(rows: List[Row]) -> Row:
    if not rows:
        return {
            "count_pairs": 0,
            "median_speedup": 0.0,
            "mean_speedup": 0.0,
            "median_time_saved_ms": 0.0,
            "mean_time_saved_ms": 0.0,
            "pct_pairs_astar_faster": 0.0,
            "pct_cost_equal": 0.0,
        }
    speeds = [float(r["speedup_d_over_a"]) for r in rows if r["speedup_d_over_a"] != float("inf")]
    saved = [float(r["time_saved_ms"]) for r in rows]
    astar_faster = sum(1 for r in rows if float(r["time_saved_ms"]) > 0.0)
    cost_equal = sum(1 for r in rows if bool(r["cost_equal"]))

    return {
        "count_pairs": len(rows),
        "median_speedup": median(speeds) if speeds else 0.0,
        "mean_speedup": mean(speeds) if speeds else 0.0,
        "median_time_saved_ms": median(saved) if saved else 0.0,
        "mean_time_saved_ms": mean(saved) if saved else 0.0,
        "pct_pairs_astar_faster": 100.0 * astar_faster / len(rows),
        "pct_cost_equal": 100.0 * cost_equal / len(rows),
    }

def write_summary(path: Path, summary: Row) -> None:
    headers = list(summary.keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerow(summary)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("results_csv", help="CSV produced by tools/parse_results.py")
    ap.add_argument("--out", required=True, help="Merged per-OD CSV output path")
    ap.add_argument("--summary", required=True, help="Summary CSV output path")
    args = ap.parse_args()

    in_path = Path(args.results_csv)
    rows = read_rows(in_path)
    merged = merge(rows)
    write_csv(Path(args.out), merged)
    write_summary(Path(args.summary), summarize(merged))
    print(f"Wrote {len(merged)} merged rows to {args.out}")
    print(f"Wrote summary to {args.summary}")

if __name__ == "__main__":
    main()
