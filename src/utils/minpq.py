"""
Minimal priority-queue helpers for shortest-path algorithms.

Wraps heapq with a push-new, skip-stale approach.
"""
from typing import Dict, List, Tuple
import heapq

Entry = Tuple[float, str]  # (distance_so_far, node)
PQ = List[Entry]

def push(q: PQ, dist: float, node: str) -> None:
    heapq.heappush(q, (float(dist), node))

def pop_min(q: PQ) -> Entry:
    return heapq.heappop(q)

def is_stale(entry: Entry, best: Dict[str, float]) -> bool:
    d, v = entry
    return d > best.get(v, float("inf"))
