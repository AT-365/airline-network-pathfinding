# Experiment results

`final_200/` contains the exact May 7 benchmark outputs used in the final report and narrated presentation.

The experiment evaluated 120 origin-destination pairs, divided into 40 short-, 40 medium-, and 40 long-haul routes. Each algorithm ran 200 times per pair.

## Main files

- `final_results_summary.csv` - overall accuracy, runtime, and expansion metrics
- `final_results_by_haul.csv` - short-, medium-, and long-haul summaries
- `final_results_merged.csv` - one Dijkstra-versus-A* comparison row per OD pair
- `final_results_all.csv` - complete per-algorithm benchmark results
- `figures/` - report-matching charts and airline-network visualization

The algorithms produced 100% shortest-path cost agreement. Dijkstra expanded 9.325 nodes on average versus 2.392 for A*, a 74.35% mean reduction. A* expanded fewer nodes on 85% of all pairs and every medium- and long-haul pair.

Runtime values are machine-sensitive because the graph is small and individual measurements are close to Python's timing-noise floor. Reproducing the experiment may yield different timing values while preserving the deterministic path-cost and expansion results.
