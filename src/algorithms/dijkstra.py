"""
Dijkstra's algorithm from scratch using a binary min-heap priority queue.
"""
from math import inf
from typing import Dict, List, Optional, Tuple

from src.algorithms.paths import reconstruct_path
from src.utils.minpq import PQ, is_stale, pop_min, push

Adj = Dict[str, List[Tuple[str, float]]]
Stats = Dict[str, int]


def _all_nodes(adj: Adj) -> set[str]:
    nodes: set[str] = set(adj.keys())
    for nbrs in adj.values():
        for v, _ in nbrs:
            nodes.add(v)
    return nodes


def dijkstra_with_stats(
    adj: Adj, source: str, target: Optional[str] = None
) -> Tuple[Dict[str, float], Dict[str, Optional[str]], Stats]:
    """Run Dijkstra and return distance map, parent map, and expansion stats."""
    nodes = _all_nodes(adj)
    dist: Dict[str, float] = {v: inf for v in nodes}
    parent: Dict[str, Optional[str]] = {v: None for v in nodes}
    stats: Stats = {"expanded_nodes": 0, "relaxations": 0, "heap_pushes": 0}

    if source not in nodes:
        return dist, parent, stats

    dist[source] = 0.0
    q: PQ = []
    push(q, 0.0, source)
    stats["heap_pushes"] += 1
    expanded: set[str] = set()

    while q:
        d_u, u = pop_min(q)
        if is_stale((d_u, u), dist):
            continue
        if u in expanded:
            continue

        expanded.add(u)
        stats["expanded_nodes"] += 1

        if target is not None and u == target:
            break

        for v, w in adj.get(u, []):
            stats["relaxations"] += 1
            alt = d_u + float(w)
            if alt < dist[v]:
                dist[v] = alt
                parent[v] = u
                push(q, alt, v)
                stats["heap_pushes"] += 1

    return dist, parent, stats


def dijkstra(adj: Adj, source: str, target: Optional[str] = None) -> Tuple[Dict[str, float], Dict[str, Optional[str]]]:
    """Backward-compatible Dijkstra wrapper."""
    dist, parent, _ = dijkstra_with_stats(adj, source, target)
    return dist, parent


def shortest_path(adj: Adj, source: str, target: str):
    dist, parent = dijkstra(adj, source, target)
    path = reconstruct_path(parent, source, target)
    cost = dist.get(target, inf) if path else float("inf")
    return cost, path


def shortest_path_with_stats(adj: Adj, source: str, target: str):
    dist, parent, stats = dijkstra_with_stats(adj, source, target)
    path = reconstruct_path(parent, source, target)
    cost = dist.get(target, inf) if path else float("inf")
    return cost, path, stats
