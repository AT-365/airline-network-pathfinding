"""
Path utilities for shortest-path algorithms.
"""
from typing import Dict, List, Optional, Tuple

Adj = Dict[str, List[Tuple[str, float]]]

def reconstruct_path(parent: Dict[str, Optional[str]], source: str, target: str) -> List[str]:
    if source == target:
        return [source]
    path: List[str] = []
    v: Optional[str] = target
    visited = set()
    while v is not None and v not in visited:
        path.append(v)
        if v == source:
            path.reverse()
            return path
        visited.add(v)
        v = parent.get(v)
    return []

def path_cost(adj: Adj, path: List[str]) -> float:
    if len(path) < 2:
        return 0.0
    total = 0.0
    for u, v in zip(path, path[1:]):
        found = False
        for w, wt in adj.get(u, []):
            if w == v:
                total += float(wt)
                found = True
                break
        if not found:
            return float("inf")
    return total
