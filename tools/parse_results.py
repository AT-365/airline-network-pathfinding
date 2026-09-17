"""
Parse benchmark output lines into CSV.

This parser supports both older single-run lines and the revised repeated-run
format produced by bench/runner.py.

Supported examples:
  DIJKSTRA ATL->LAX time=12.34 ms cost=3125.8 km hops=1 OK
  ASTAR ATL->LAX mean_time=0.0450 ms median_time=0.0400 ms cost=3125.8 km hops=1 expanded=2 relaxations=8 runs=200 OK

Usage:
  python tools/parse_results.py results_dijkstra.txt results_astar.txt --out parsed_results.csv
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator

CURRENT_RE = re.compile(
    r"""^\s*
        (?P<algo>[A-Za-z\*\+]+)\s+
        (?P<src>[A-Za-z0-9]{3})\s*->\s*(?P<dst>[A-Za-z0-9]{3})\s+
        mean_time=(?P<mean_time_ms>[0-9]+(?:\.[0-9]+)?)\s*ms\s+
        median_time=(?P<median_time_ms>[0-9]+(?:\.[0-9]+)?)\s*ms\s+
        cost=(?P<cost_km>inf|[0-9]+(?:\.[0-9]+)?)\s*km\s+
        hops=(?P<hops>[0-9]+)\s+
        expanded=(?P<expanded_nodes>[0-9]+)\s+
        relaxations=(?P<relaxations>[0-9]+)\s+
        runs=(?P<runs>[0-9]+)\s+
        (?P<status>\w+)\s*$
    """,
    re.VERBOSE | re.IGNORECASE,
)

LEGACY_RE = re.compile(
    r"""^\s*
        (?P<algo>[A-Za-z\*\+]+)\s+
        (?P<src>[A-Za-z0-9]{3})\s*->\s*(?P<dst>[A-Za-z0-9]{3})\s+
        time=(?P<time_ms>[0-9]+(?:\.[0-9]+)?)\s*ms\s+
        cost=(?P<cost_km>inf|[0-9]+(?:\.[0-9]+)?)\s*km\s+
        hops=(?P<hops>[0-9]+)\s+
        (?P<status>\w+)\s*$
    """,
    re.VERBOSE | re.IGNORECASE,
)

HEADERS = [
    "algo", "src", "dst", "mean_time_ms", "median_time_ms", "cost_km", "hops",
    "expanded_nodes", "relaxations", "runs", "status",
]


def _float_cost(value: str) -> float:
    return float("inf") if value.lower() == "inf" else float(value)


def parse_lines(lines: Iterable[str]) -> Iterator[Dict[str, Any]]:
    for line in lines:
        m = CURRENT_RE.match(line)
        if m:
            d = m.groupdict()
            yield {
                "algo": d["algo"].upper(),
                "src": d["src"].upper(),
                "dst": d["dst"].upper(),
                "mean_time_ms": float(d["mean_time_ms"]),
                "median_time_ms": float(d["median_time_ms"]),
                "cost_km": _float_cost(d["cost_km"]),
                "hops": int(d["hops"]),
                "expanded_nodes": int(d["expanded_nodes"]),
                "relaxations": int(d["relaxations"]),
                "runs": int(d["runs"]),
                "status": d["status"].upper(),
            }
            continue

        m = LEGACY_RE.match(line)
        if m:
            d = m.groupdict()
            time_ms = float(d["time_ms"])
            yield {
                "algo": d["algo"].upper(),
                "src": d["src"].upper(),
                "dst": d["dst"].upper(),
                "mean_time_ms": time_ms,
                "median_time_ms": time_ms,
                "cost_km": _float_cost(d["cost_km"]),
                "hops": int(d["hops"]),
                "expanded_nodes": "",
                "relaxations": "",
                "runs": 1,
                "status": d["status"].upper(),
            }


def parse_file(path: Path) -> Iterator[Dict[str, Any]]:
    data = path.read_bytes()
    encoding = "utf-16" if data.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8"
    text = data.decode(encoding, errors="replace")
    yield from parse_lines(text.splitlines())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", help="One or more runner output text files to parse.")
    parser.add_argument("--out", required=True, help="Output CSV path.")
    args = parser.parse_args()

    rows: list[Dict[str, Any]] = []
    for inp in args.inputs:
        rows.extend(parse_file(Path(inp)))
    rows.sort(key=lambda r: (r["src"], r["dst"], r["algo"]))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
