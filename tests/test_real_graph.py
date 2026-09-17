import math
import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.algorithms.astar import shortest_path_astar, shortest_path_astar_with_stats
from src.algorithms.dijkstra import shortest_path, shortest_path_with_stats
from src.graph.loader import load_graph


def resolve_project_path(env_name: str, default_name: str) -> Path:
    raw_value = os.environ.get(env_name)
    path = Path(raw_value) if raw_value else PROJECT_ROOT / default_name
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


NODES = resolve_project_path("NODES_CSV", "data/nodes.csv")
EDGES = resolve_project_path("EDGES_CSV", "data/edges.csv")
OD_PAIRS = resolve_project_path("OD_PAIRS_TXT", "data/od_pairs.txt")


@pytest.mark.skipif(not (NODES.exists() and EDGES.exists()), reason="nodes.csv/edges.csv not found")
def test_real_graph_atl_lax_costs_match():
    adj, coords = load_graph(str(NODES), str(EDGES))
    cost_d, path_d = shortest_path(adj, "ATL", "LAX")
    cost_a, path_a = shortest_path_astar(adj, coords, "ATL", "LAX")
    assert path_d and path_a
    assert math.isfinite(cost_d) and cost_d > 0.0
    assert math.isfinite(cost_a) and cost_a > 0.0
    assert math.isclose(cost_a, cost_d, abs_tol=1e-6)


@pytest.mark.skipif(not (NODES.exists() and EDGES.exists()), reason="nodes.csv/edges.csv not found")
def test_real_graph_jfk_sea_costs_match():
    adj, coords = load_graph(str(NODES), str(EDGES))
    cost_d, path_d = shortest_path(adj, "JFK", "SEA")
    cost_a, path_a = shortest_path_astar(adj, coords, "JFK", "SEA")
    assert path_d and path_a
    assert math.isfinite(cost_d) and cost_d > 0.0
    assert math.isfinite(cost_a) and cost_a > 0.0
    assert math.isclose(cost_a, cost_d, abs_tol=1e-6)


@pytest.mark.skipif(not (NODES.exists() and EDGES.exists()), reason="nodes.csv/edges.csv not found")
def test_real_graph_astar_expands_no_more_for_sample():
    adj, coords = load_graph(str(NODES), str(EDGES))
    cost_d, _path_d, stats_d = shortest_path_with_stats(adj, "ATL", "SEA")
    cost_a, _path_a, stats_a = shortest_path_astar_with_stats(adj, coords, "ATL", "SEA")
    assert math.isclose(cost_a, cost_d, abs_tol=1e-6)
    assert stats_a["expanded_nodes"] <= stats_d["expanded_nodes"]


@pytest.mark.skipif(
    not (NODES.exists() and EDGES.exists() and OD_PAIRS.exists()),
    reason="nodes.csv/edges.csv/od_pairs.txt not found",
)
def test_all_configured_od_pairs_costs_match():
    """Validate A* against Dijkstra for every OD pair used in the final experiment."""
    adj, coords = load_graph(str(NODES), str(EDGES))
    with OD_PAIRS.open(encoding="utf-8") as f:
        pairs = [line.strip().split("-") for line in f if line.strip() and not line.startswith("#")]

    assert len(pairs) == 120
    for src, dst in pairs:
        cost_d, path_d, stats_d = shortest_path_with_stats(adj, src.upper(), dst.upper())
        cost_a, path_a, stats_a = shortest_path_astar_with_stats(adj, coords, src.upper(), dst.upper())
        assert path_d and path_a, f"Missing path for {src}-{dst}"
        assert math.isclose(cost_a, cost_d, abs_tol=1e-6), f"Cost mismatch for {src}-{dst}"
        assert stats_a["expanded_nodes"] <= len(adj), f"A* expanded too many nodes for {src}-{dst}"
        assert stats_d["expanded_nodes"] <= len(adj), f"Dijkstra expanded too many nodes for {src}-{dst}"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
