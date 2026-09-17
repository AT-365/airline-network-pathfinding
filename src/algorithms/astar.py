"""
A* search from scratch on a directed, weighted graph.
"""
from math import inf
from typing import Dict, List, Optional, Tuple
import heapq

from src.algorithms.heuristics import straight_line_estimate
from src.algorithms.paths import reconstruct_path

Adj = Dict[str, List[Tuple[str, float]]]
Coords = Dict[str, Tuple[float, float]]
Stats = Dict[str, int]


def _all_nodes(adj: Adj) -> set[str]:
    nodes: set[str] = set(adj.keys())
    for nbrs in adj.values():
        for v, _ in nbrs:
            nodes.add(v)
    return nodes


def astar_with_stats(
    adj: Adj, coords: Coords, source: str, target: str
) -> Tuple[Dict[str, float], Dict[str, Optional[str]], Stats]:
    """Run A* and return distance map, parent map, and expansion stats."""
    nodes = _all_nodes(adj)
    dist: Dict[str, float] = {v: inf for v in nodes}
    parent: Dict[str, Optional[str]] = {v: None for v in nodes}
    stats: Stats = {"expanded_nodes": 0, "relaxations": 0, "heap_pushes": 0}

    if source not in nodes or target not in nodes:
        return dist, parent, stats

    dist[source] = 0.0
    h0 = straight_line_estimate(coords, source, target)
    pq: list[tuple[float, float, str]] = [(h0, 0.0, source)]
    stats["heap_pushes"] += 1
    expanded: set[str] = set()

    while pq:
        _f_u, g_u, u = heapq.heappop(pq)
        if g_u > dist[u]:
            continue
        if u in expanded:
            continue

        expanded.add(u)
        stats["expanded_nodes"] += 1

        if u == target:
            break

        for v, w in adj.get(u, []):
            stats["relaxations"] += 1
            alt_g = g_u + float(w)
            if alt_g < dist[v]:
                dist[v] = alt_g
                parent[v] = u
                f_v = alt_g + straight_line_estimate(coords, v, target)
                heapq.heappush(pq, (f_v, alt_g, v))
                stats["heap_pushes"] += 1

    return dist, parent, stats


def astar(adj: Adj, coords: Coords, source: str, target: str) -> Tuple[Dict[str, float], Dict[str, Optional[str]]]:
    """Backward-compatible A* wrapper."""
    dist, parent, _ = astar_with_stats(adj, coords, source, target)
    return dist, parent


def shortest_path_astar(adj: Adj, coords: Coords, source: str, target: str):
    dist, parent = astar(adj, coords, source, target)
    path = reconstruct_path(parent, source, target)
    cost = dist.get(target, inf) if path else float("inf")
    return cost, path


def shortest_path_astar_with_stats(adj: Adj, coords: Coords, source: str, target: str):
    dist, parent, stats = astar_with_stats(adj, coords, source, target)
    path = reconstruct_path(parent, source, target)
    cost = dist.get(target, inf) if path else float("inf")
    return cost, path, stats
