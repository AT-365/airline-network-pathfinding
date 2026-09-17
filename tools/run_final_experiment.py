"""
Run the final Dijkstra vs A* experiment for the airline network project.

This script produces reproducible CSV outputs for:
- per-algorithm repeated-run timing results
- merged Dijkstra vs A* comparisons
- overall summary metrics
- haul-category summary metrics
- chart PNG files
"""
from __future__ import annotations

import argparse
import builtins
import csv
import math
import sys
import time
from pathlib import Path
from statistics import mean, median, stdev
from typing import Any, Callable, Dict, Iterable, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.algorithms.astar import shortest_path_astar_with_stats
from src.algorithms.dijkstra import shortest_path_with_stats
from src.algorithms.heuristics import straight_line_estimate
from src.graph.loader import load_graph

Adj = Dict[str, List[Tuple[str, float]]]
Coords = Dict[str, Tuple[float, float]]
Row = Dict[str, Any]


def resolve_project_path(raw_path: str) -> Path:
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def filesystem_path(path: Path) -> str:
    resolved = path.resolve(strict=False)
    raw = str(resolved)
    if sys.platform != "win32" or len(raw) < 240 or raw.startswith("\\\\?\\"):
        return raw
    if raw.startswith("\\\\"):
        return "\\\\?\\UNC\\" + raw.lstrip("\\")
    return "\\\\?\\" + raw


def read_od_pairs(path: Path) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for line in Path(filesystem_path(path)).read_text(encoding="utf-8").splitlines():
        cleaned = line.strip().replace(",", "-").replace(" ", "-")
        if not cleaned or cleaned.startswith("#"):
            continue
        parts = [p.strip().upper() for p in cleaned.split("-") if p.strip()]
        if len(parts) == 2:
            pairs.append((parts[0], parts[1]))
    return pairs


def assign_equal_thirds(pairs: list[tuple[str, str]], coords: Coords) -> dict[tuple[str, str], tuple[str, float]]:
    distances: list[tuple[float, tuple[str, str]]] = []
    for src, dst in pairs:
        distances.append((straight_line_estimate(coords, src, dst), (src, dst)))
    distances.sort(key=lambda item: item[0])

    labeled: dict[tuple[str, str], tuple[str, float]] = {}
    n = len(distances)
    first_cut = n // 3
    second_cut = (2 * n) // 3
    for index, (direct_km, pair) in enumerate(distances):
        if index < first_cut:
            category = "short"
        elif index < second_cut:
            category = "medium"
        else:
            category = "long"
        labeled[pair] = (category, direct_km)
    return labeled


def measure(
    algorithm: str,
    func: Callable[..., tuple[float, list[str], dict[str, int]]],
    args: tuple[Any, ...],
    runs: int,
) -> tuple[float, float, float, float, list[str], dict[str, int]]:
    # One warmup run keeps import/cache effects out of the recorded timing loop.
    cost, path, stats = func(*args)
    times: list[float] = []
    for _ in range(runs):
        start = time.perf_counter()
        cost, path, stats = func(*args)
        times.append((time.perf_counter() - start) * 1000.0)

    time_stdev = stdev(times) if len(times) > 1 else 0.0
    return mean(times), median(times), min(times), time_stdev, path, stats


def run_experiment(adj: Adj, coords: Coords, pairs: list[tuple[str, str]], runs: int) -> tuple[list[Row], list[Row]]:
    labels = assign_equal_thirds(pairs, coords)
    all_rows: list[Row] = []
    merged_rows: list[Row] = []

    for src, dst in pairs:
        category, direct_km = labels[(src, dst)]
        d_mean, d_med, d_min, d_sd, d_path, d_stats = measure(
            "DIJKSTRA", shortest_path_with_stats, (adj, src, dst), runs
        )
        a_mean, a_med, a_min, a_sd, a_path, a_stats = measure(
            "ASTAR", shortest_path_astar_with_stats, (adj, coords, src, dst), runs
        )

        d_cost, _d_path_check, _ = shortest_path_with_stats(adj, src, dst)
        a_cost, _a_path_check, _ = shortest_path_astar_with_stats(adj, coords, src, dst)
        d_hops = max(0, len(d_path) - 1)
        a_hops = max(0, len(a_path) - 1)
        status_d = "OK" if d_path else "UNREACHABLE"
        status_a = "OK" if a_path else "UNREACHABLE"

        all_rows.extend([
            {
                "algo": "DIJKSTRA", "src": src, "dst": dst, "haul_category": category,
                "direct_distance_km": direct_km, "runs": runs,
                "mean_time_ms": d_mean, "median_time_ms": d_med, "min_time_ms": d_min, "stdev_time_ms": d_sd,
                "cost_km": d_cost, "hops": d_hops, "expanded_nodes": d_stats["expanded_nodes"],
                "relaxations": d_stats["relaxations"], "heap_pushes": d_stats["heap_pushes"], "status": status_d,
            },
            {
                "algo": "ASTAR", "src": src, "dst": dst, "haul_category": category,
                "direct_distance_km": direct_km, "runs": runs,
                "mean_time_ms": a_mean, "median_time_ms": a_med, "min_time_ms": a_min, "stdev_time_ms": a_sd,
                "cost_km": a_cost, "hops": a_hops, "expanded_nodes": a_stats["expanded_nodes"],
                "relaxations": a_stats["relaxations"], "heap_pushes": a_stats["heap_pushes"], "status": status_a,
            },
        ])

        cost_diff = abs(a_cost - d_cost)
        mean_saved = d_mean - a_mean
        median_saved = d_med - a_med
        expansion_saved = d_stats["expanded_nodes"] - a_stats["expanded_nodes"]
        relaxation_saved = d_stats["relaxations"] - a_stats["relaxations"]
        speedup_mean = d_mean / a_mean if a_mean > 0 else float("inf")
        speedup_median = d_med / a_med if a_med > 0 else float("inf")
        pct_time_reduction_mean = (1.0 - (a_mean / d_mean)) * 100.0 if d_mean > 0 else 0.0
        pct_expansion_reduction = (expansion_saved / d_stats["expanded_nodes"] * 100.0) if d_stats["expanded_nodes"] > 0 else 0.0

        merged_rows.append({
            "src": src, "dst": dst, "haul_category": category, "direct_distance_km": direct_km, "runs": runs,
            "dijkstra_mean_time_ms": d_mean, "astar_mean_time_ms": a_mean,
            "dijkstra_median_time_ms": d_med, "astar_median_time_ms": a_med,
            "dijkstra_cost_km": d_cost, "astar_cost_km": a_cost,
            "cost_equal": cost_diff <= 1e-6, "cost_diff_km": cost_diff,
            "dijkstra_hops": d_hops, "astar_hops": a_hops,
            "dijkstra_expanded_nodes": d_stats["expanded_nodes"], "astar_expanded_nodes": a_stats["expanded_nodes"],
            "expanded_nodes_saved_by_astar": expansion_saved,
            "pct_expansion_reduction": pct_expansion_reduction,
            "dijkstra_relaxations": d_stats["relaxations"], "astar_relaxations": a_stats["relaxations"],
            "relaxations_saved_by_astar": relaxation_saved,
            "speedup_mean_d_over_a": speedup_mean,
            "speedup_median_d_over_a": speedup_median,
            "mean_time_saved_ms": mean_saved,
            "median_time_saved_ms": median_saved,
            "pct_time_reduction_mean": pct_time_reduction_mean,
        })

    return all_rows, merged_rows


def write_csv(path: Path, rows: list[Row]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with builtins.open(filesystem_path(path), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def overall_summary(rows: list[Row]) -> list[Row]:
    if not rows:
        return []
    return [{
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
        "median_dijkstra_expanded_nodes": median([r["dijkstra_expanded_nodes"] for r in rows]),
        "median_astar_expanded_nodes": median([r["astar_expanded_nodes"] for r in rows]),
        "mean_expanded_nodes_saved_by_astar": mean([r["expanded_nodes_saved_by_astar"] for r in rows]),
        "median_expanded_nodes_saved_by_astar": median([r["expanded_nodes_saved_by_astar"] for r in rows]),
        "pct_pairs_astar_fewer_expansions": 100.0 * sum(1 for r in rows if r["expanded_nodes_saved_by_astar"] > 0) / len(rows),
    }]


def category_summary(rows: list[Row]) -> list[Row]:
    out: list[Row] = []
    for category in ["short", "medium", "long"]:
        subset = [r for r in rows if r["haul_category"] == category]
        if not subset:
            continue
        out.append({
            "haul_category": category,
            "count_pairs": len(subset),
            "pct_cost_equal": 100.0 * sum(1 for r in subset if r["cost_equal"]) / len(subset),
            "mean_dijkstra_time_ms": mean([r["dijkstra_mean_time_ms"] for r in subset]),
            "mean_astar_time_ms": mean([r["astar_mean_time_ms"] for r in subset]),
            "median_dijkstra_time_ms": median([r["dijkstra_median_time_ms"] for r in subset]),
            "median_astar_time_ms": median([r["astar_median_time_ms"] for r in subset]),
            "mean_time_saved_ms": mean([r["mean_time_saved_ms"] for r in subset]),
            "pct_pairs_astar_faster_mean_time": 100.0 * sum(1 for r in subset if r["mean_time_saved_ms"] > 0) / len(subset),
            "mean_dijkstra_expanded_nodes": mean([r["dijkstra_expanded_nodes"] for r in subset]),
            "mean_astar_expanded_nodes": mean([r["astar_expanded_nodes"] for r in subset]),
            "mean_expanded_nodes_saved_by_astar": mean([r["expanded_nodes_saved_by_astar"] for r in subset]),
            "pct_pairs_astar_fewer_expansions": 100.0 * sum(1 for r in subset if r["expanded_nodes_saved_by_astar"] > 0) / len(subset),
        })
    return out


def plot_grouped_bar(categories: list[str], d_values: list[float], a_values: list[float], ylabel: str, title: str, out_path: Path) -> None:
    x = list(range(len(categories)))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar([i - width / 2 for i in x], d_values, width, label="Dijkstra")
    ax.bar([i + width / 2 for i in x], a_values, width, label="A*")
    ax.set_xticks(x)
    ax.set_xticklabels([c.capitalize() for c in categories])
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(filesystem_path(out_path), dpi=200)
    plt.close(fig)


def make_charts(cat_rows: list[Row], out_dir: Path) -> None:
    categories = [r["haul_category"] for r in cat_rows]
    plot_grouped_bar(
        categories,
        [r["mean_dijkstra_time_ms"] for r in cat_rows],
        [r["mean_astar_time_ms"] for r in cat_rows],
        "Mean runtime (ms)",
        "Mean Runtime by Haul Category",
        out_dir / "figure_1_mean_runtime_by_haul.png",
    )
    plot_grouped_bar(
        categories,
        [r["median_dijkstra_time_ms"] for r in cat_rows],
        [r["median_astar_time_ms"] for r in cat_rows],
        "Median runtime (ms)",
        "Median Runtime by Haul Category",
        out_dir / "figure_2_median_runtime_by_haul.png",
    )
    plot_grouped_bar(
        categories,
        [r["mean_dijkstra_expanded_nodes"] for r in cat_rows],
        [r["mean_astar_expanded_nodes"] for r in cat_rows],
        "Mean expanded nodes",
        "Mean Node Expansions by Haul Category",
        out_dir / "figure_3_mean_node_expansions_by_haul.png",
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar([c.capitalize() for c in categories], [r["mean_expanded_nodes_saved_by_astar"] for r in cat_rows])
    ax.set_ylabel("Mean expanded nodes saved")
    ax.set_title("Average Node Expansions Saved by A*")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(filesystem_path(out_dir / "figure_4_node_expansions_saved_by_astar.png"), dpi=200)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nodes", default="data/nodes.csv")
    parser.add_argument("--edges", default="data/edges.csv")
    parser.add_argument("--od", default="data/od_pairs.txt")
    parser.add_argument("--runs", type=int, default=20)
    parser.add_argument("--outdir", default="results/final")
    args = parser.parse_args()

    nodes_path = resolve_project_path(args.nodes)
    edges_path = resolve_project_path(args.edges)
    od_path = resolve_project_path(args.od)
    out_dir = resolve_project_path(args.outdir)

    adj, coords = load_graph(filesystem_path(nodes_path), filesystem_path(edges_path))
    pairs = read_od_pairs(od_path)
    all_rows, merged_rows = run_experiment(adj, coords, pairs, max(1, args.runs))
    figures_dir = out_dir / "figures"
    summary_rows = overall_summary(merged_rows)
    cat_rows = category_summary(merged_rows)

    write_csv(out_dir / "final_results_all.csv", all_rows)
    write_csv(out_dir / "final_results_merged.csv", merged_rows)
    write_csv(out_dir / "final_results_summary.csv", summary_rows)
    write_csv(out_dir / "final_results_by_haul.csv", cat_rows)
    make_charts(cat_rows, figures_dir)

    print(f"Wrote final results to {out_dir}")
    print(f"Wrote figures to {figures_dir}")
    if summary_rows:
        s = summary_rows[0]
        print("Summary:")
        print(f"  Cost agreement: {s['pct_cost_equal']:.1f}%")
        print(f"  A* faster by mean runtime: {s['pct_pairs_astar_faster_mean_time']:.2f}% of pairs")
        print(f"  A* fewer expansions: {s['pct_pairs_astar_fewer_expansions']:.2f}% of pairs")
        print(f"  Mean expansions Dijkstra/A*: {s['mean_dijkstra_expanded_nodes']:.2f} / {s['mean_astar_expanded_nodes']:.2f}")


if __name__ == "__main__":
    main()
