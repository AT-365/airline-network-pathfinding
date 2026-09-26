# Airline Network Pathfinding: Dijkstra vs. A*

[![Tests](https://github.com/AT-365/airline-network-pathfinding/actions/workflows/tests.yml/badge.svg)](https://github.com/AT-365/airline-network-pathfinding/actions/workflows/tests.yml)

A reproducible Python experiment comparing Dijkstra's algorithm and A* search on a directed U.S. airline network. The project models 20 major airports as vertices, historical direct routes as weighted edges, and uses Haversine distance as a geographic heuristic for A*.

**Research Question:** Can heuristic guidance reduce the amount of graph search without sacrificing the optimal route cost?

**Key Finding:** A* expanded 74.35% fewer nodes than Dijkstra on average while maintaining 100% shortest-path cost agreement across all 120 test pairs.

## Why This Project Matters

This project demonstrates practical algorithms and optimization skills that employers value:

- implementing classical graph algorithms from scratch
- understanding heuristic design and its impact on search performance
- rigorous experimental design with stratified evaluation
- honest reporting of results (performance gains and limitations)
- reproducible science with automated testing and benchmarking
- clear communication of trade-offs and caveats

## Project Overview

The experiment compares two pathfinding algorithms on a realistic graph:

**Graph:** 20 U.S. airports, 293 directed routes, Haversine-based edge weights

**Algorithms:**
- **Dijkstra:** Unguided best-first search using a priority queue
- **A*:** Guided best-first search with Haversine distance heuristic

**Evaluation:** 120 origin-destination pairs (40 short-haul, 40 medium-haul, 40 long-haul), 200 runs per pair per algorithm

**Metrics:** Node expansions, path cost agreement, runtime, expansion reduction

## Verified Results

| Measure | Result |
|---|---:|
| Airport nodes | 20 |
| Directed routes | 293 |
| Origin-destination pairs tested | 120 |
| Timing runs per pair, per algorithm | 200 |
| Shortest-path cost agreement | 100% |
| Mean nodes expanded by Dijkstra | 9.325 |
| Mean nodes expanded by A* | 2.392 |
| Mean expansion reduction | 74.35% |
| Pairs where A* expanded fewer nodes | 85.0% |
| Pairs where A* was faster by mean runtime | 56.7% |
| Mean Dijkstra/A* runtime ratio | 2.440x |

**Important Note:** Runtime values on small graphs are extremely close to Python's timing-noise floor. The most reliable result is the **74.35% reduction in node expansions**—a fundamental algorithmic advantage that is less sensitive to machine variation.

## What I Built

- **Directed adjacency-list graph model** for airport-route data with Haversine-based weights
- **Dijkstra implementation** using a binary min-heap priority queue
- **A* implementation** with f(n) = g(n) + h(n) and Haversine heuristic
- **Path reconstruction algorithm** with route-cost validation
- **Instrumentation system** tracking node expansions, relaxations, heap operations, hops, and runtime
- **Stratified evaluation framework** dividing routes by distance category
- **Comprehensive test suite** covering toy graphs, real-network pairs, and aggregate benchmark validation
- **Reproducible outputs** as CSV summaries and Matplotlib visualizations

## Technologies & Methods

- **Python 3.13:** Algorithm implementation, experiment automation, data processing
- **heapq:** Binary min-heap priority queue operations (both algorithms)
- **Custom priority-queue helper:** Dijkstra queue abstraction
- **Haversine formula:** Geographic edge weights and A* heuristic calculation
- **Matplotlib:** Benchmark charts and network visualization
- **pandas:** Result aggregation and analysis
- **NetworkX:** Graph structure and visualization support
- **pytest:** Correctness and regression testing
- **CSV and pathlib:** Reproducible file handling and data loading
- **GitHub Actions:** Automated test execution on every push

## Quick Start

Clone and set up the environment:

```bash
git clone https://github.com/AT-365/airline-network-pathfinding.git
cd airline-network-pathfinding
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

Run the automated tests:

```bash
python -m pytest -q
```

Reproduce the complete benchmark (generates results in a new folder):

```bash
python tools/run_final_experiment.py --runs 200 --outdir results/reproduced_200
```

Run one route interactively:

```bash
python bench/runner.py --nodes data/nodes.csv --edges data/edges.csv --algo astar --od ATL-SEA
```

## Experiment Outputs

The repository includes the exact May 7 benchmark outputs used in the final report and presentation:

- [Overall summary](results/final_200/final_results_summary.csv) - aggregate metrics across all pairs
- [Results by haul category](results/final_200/final_results_by_haul.csv) - performance broken down by route distance
- [Merged pair-level comparison](results/final_200/final_results_merged.csv) - Dijkstra vs. A* for each OD pair
- [All repeated-run results](results/final_200/final_results_all.csv) - complete per-algorithm detailed results
- [Annotated OD-pair workbook](data/od_pairs_annotated.xlsx) - pair configuration and validation
- [All charts](results/final_200/figures/) - visualizations from the final report

## Repository Map

| Path | Purpose |
|---|---|
| `src/algorithms/` | Dijkstra, A*, Haversine heuristic, path reconstruction |
| `src/graph/` | CSV graph loader, graph representation, visualization |
| `src/utils/` | Haversine distance calculator, priority-queue helpers |
| `tools/` | Complete benchmark runner, result parsing, comparison tools |
| `bench/` | Interactive command-line route runner |
| `tests/` | Toy-graph tests, real-route tests, all-pair validation |
| `data/` | Airport nodes, directed edges, OD pairs, annotated workbook |
| `results/final_200/` | Report-matching CSV outputs and Matplotlib figures |
| `portfolio/` | Final graded report and presentation artifacts |

## How to Review This Project

For a quick technical review:

1. Read this README.
2. Review [`src/algorithms/dijkstra.py`](src/algorithms/dijkstra.py) and [`src/algorithms/astar.py`](src/algorithms/astar.py).
3. Inspect [`src/algorithms/heuristics.py`](src/algorithms/heuristics.py) to see Haversine distance calculation.
4. Review [`tests/test_real_graph.py`](tests/test_real_graph.py) to understand validation approach.
5. Examine [`results/final_200/final_results_summary.csv`](results/final_200/final_results_summary.csv) for aggregate results.
6. View the visualizations in [`results/final_200/figures/`](results/final_200/figures/).
7. Read [`portfolio/final_report.pdf`](portfolio/final_report.pdf) for complete analysis.

For the presentation: Download [`portfolio/`](portfolio/) and open the narrated PowerPoint (`.ppsx`) in desktop PowerPoint to hear the 15-minute presentation audio.

## What I Learned

This project taught me important lessons about algorithmic design and honest experimental evaluation:

- **Heuristic quality directly impacts search efficiency, but guarantees matter.** A* is faster when h(n) is admissible (never overestimates), but a poor heuristic can make it slower than Dijkstra. Haversine distance worked well because it's a valid lower bound on actual travel distance.

- **Small graphs expose timing noise.** On a 20-node network, individual millisecond measurements are unreliable. The node-expansion metric is far more stable and informative—it measures algorithmic efficiency independent of machine conditions.

- **Stratified evaluation reveals hidden patterns.** Breaking results into short-, medium-, and long-haul categories showed that A*'s advantage is stronger on longer routes. A uniform average would have hidden this insight.

- **100% agreement on one metric doesn't mean the algorithms are equivalent.** Both Dijkstra and A* found optimal paths, but A* required 74% fewer node expansions. The choice of metric completely changes the story.

## Project Context

This project was completed for **CSCI 7242 — Algorithm Design and Analysis** as a graduate computer science capstone. It combines theoretical algorithm knowledge with practical implementation and rigorous experimental methodology.

The data is sourced from historical OpenFlights records and is used for educational purposes only. The network is static and not current; results should not be interpreted as live route-planning advice.

## Data Note

The airline network is a static experimental sample derived from historical OpenFlights airport and route records. It is not a current airline schedule. The results should not be interpreted as live route-planning advice or predictions about actual flight times.

## Author

Autenia Murray  
M.S. Computer Science candidate, Data & Knowledge Systems  
Georgia Southern University
