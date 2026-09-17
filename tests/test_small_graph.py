import math
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.algorithms.astar import shortest_path_astar
from src.algorithms.dijkstra import shortest_path


def test_toy_graph_dijkstra_shortest_path():
    adj = {
        "A": [("B", 1.0), ("C", 4.0)],
        "B": [("C", 2.0), ("D", 5.0)],
        "C": [("D", 1.0)],
        "D": [],
    }
    cost, path = shortest_path(adj, "A", "D")
    assert path == ["A", "B", "C", "D"]
    assert math.isclose(cost, 4.0, rel_tol=1e-9)


def test_toy_graph_astar_matches_dijkstra():
    adj = {
        "A": [("B", 1.0), ("C", 4.0)],
        "B": [("C", 2.0), ("D", 5.0)],
        "C": [("D", 1.0)],
        "D": [],
    }
    coords = {
        "A": (0.0, 0.0),
        "B": (0.0, 0.0),
        "C": (0.0, 0.0),
        "D": (0.0, 0.0),
    }
    cost_d, path_d = shortest_path(adj, "A", "D")
    cost_a, path_a = shortest_path_astar(adj, coords, "A", "D")
    assert path_a == path_d
    assert math.isclose(cost_a, cost_d, rel_tol=1e-9)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
