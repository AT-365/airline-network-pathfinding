"""
Benchmark runner for Dijkstra and A*.

Outputs path cost, hops, runtime, and node-expansion statistics.
"""
import argparse
import sys
import time
from pathlib import Path
from statistics import mean, median
from typing import Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.algorithms.astar import shortest_path_astar_with_stats
from src.algorithms.dijkstra import shortest_path_with_stats as dijkstra_sp_with_stats
from src.graph.loader import load_graph


def parse_od(s: str) -> Tuple[str, str]:
    s = s.strip().replace(",", "-").replace(" ", "-")
    parts = [p for p in s.split("-") if p]
    if len(parts) != 2:
        raise argparse.ArgumentTypeError(f"Invalid OD format: {s!r}. Use SRC-DST, e.g., ATL-LAX.")
    return parts[0].upper(), parts[1].upper()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nodes", required=True)
    ap.add_argument("--edges", required=True)
    ap.add_argument("--algo", choices=["dijkstra", "astar"], default="dijkstra")
    ap.add_argument("--od", nargs="+", type=parse_od, required=True)
    ap.add_argument("--runs", type=int, default=20, help="Number of timing runs per OD pair.")
    args = ap.parse_args()

    adj, coords = load_graph(args.nodes, args.edges)

    for s, t in args.od:
        times: list[float] = []
        cost = float("inf")
        path: list[str] = []
        stats = {"expanded_nodes": 0, "relaxations": 0, "heap_pushes": 0}

        for _ in range(max(1, args.runs)):
            start = time.perf_counter()
            if args.algo == "dijkstra":
                cost, path, stats = dijkstra_sp_with_stats(adj, s, t)
            else:
                cost, path, stats = shortest_path_astar_with_stats(adj, coords, s, t)
            times.append((time.perf_counter() - start) * 1000.0)

        hops = max(0, len(path) - 1)
        status = "OK" if path else "UNREACHABLE"
        print(
            f"{args.algo.upper()} {s}->{t} "
            f"mean_time={mean(times):.4f} ms "
            f"median_time={median(times):.4f} ms "
            f"cost={cost:.6f} km "
            f"hops={hops} "
            f"expanded={stats['expanded_nodes']} "
            f"relaxations={stats['relaxations']} "
            f"runs={max(1, args.runs)} "
            f"{status}"
        )


if __name__ == "__main__":
    main()
