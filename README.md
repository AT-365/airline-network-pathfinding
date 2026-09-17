# Airline Network Pathfinding: Dijkstra vs. A*

[![Tests](https://github.com/AT-365/airline-network-pathfinding/actions/workflows/tests.yml/badge.svg)](https://github.com/AT-365/airline-network-pathfinding/actions/workflows/tests.yml)

A reproducible comparison of Dijkstra's algorithm and A* on a directed, weighted U.S. airline network. The project models airports as vertices, historical direct routes as edges, and Haversine great-circle distance as edge weight. Both algorithms were implemented from scratch in Python and evaluated on the same 120 origin-destination pairs.

## Results at a glance

- **20 airports and 293 directed routes** in a controlled historical hub-network sample
- **120 origin-destination pairs**, evenly divided into short-, medium-, and long-haul groups
- **200 timed runs per pair per algorithm** in the submitted experiment
- **100% shortest-path cost agreement** between Dijkstra and A*
- **A\* expanded fewer nodes on 85% of pairs**
- Mean nodes expanded: **9.325 for Dijkstra vs. 2.392 for A\***

Runtime differences are intentionally interpreted cautiously: the graph is small and measured times are near Python's timing-noise floor. The more stable finding is that A* reaches the same optimal cost while exploring substantially fewer nodes, especially on medium- and long-haul pairs.

![Mean node expansions by haul category](results/final_200/figures/figure_3_mean_node_expansions_by_haul.png)

## What this demonstrates

- Graph modeling with airport and route data
- Dijkstra and A* implementations using binary-heap priority queues
- An admissible geographic heuristic based on Haversine distance
- Automated correctness testing across every configured OD pair
- Repeated-run benchmarking with runtime, path cost, hop, expansion, relaxation, and heap-push metrics
- Reproducible CSV outputs and Matplotlib visualizations

## Repository map

| Path | Purpose |
|---|---|
| `src/algorithms/` | Dijkstra, A*, heuristic, and path reconstruction |
| `src/graph/` | CSV graph loader and network visualization |
| `src/utils/` | Haversine distance and priority-queue helpers |
| `tools/run_final_experiment.py` | End-to-end 200-run experiment and chart generation |
| `tests/` | Toy-graph, real-route, and all-120-pair validation |
| `data/` | Curated airport nodes, directed edges, and OD pairs |
| `results/final_200/` | Submitted benchmark results |
| `portfolio/` | Final report and supporting artifact notes |

## Quick start

```bash
git clone https://github.com/AT-365/airline-network-pathfinding.git
cd airline-network-pathfinding
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python -m pytest -q
```

Run the complete benchmark:

```bash
python tools/run_final_experiment.py --runs 200 --outdir results/reproduced_200
```

Run one route interactively:

```bash
python bench/runner.py --nodes data/nodes.csv --edges data/edges.csv --algo astar --od ATL-SEA
```

## Portfolio artifacts

- [Final project report](portfolio/final_report.pdf)

The report explains the research question, experimental design, validation strategy, limitations, and interpretation of results.

## Data note

The network is a static experimental sample derived from historical OpenFlights airport and route records; it is not a current airline schedule. Results support algorithm comparison on this graph and should not be interpreted as live route-planning advice.

## Author

Autenia Murray — M.S. Computer Science candidate, Data & Knowledge Systems
