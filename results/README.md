# Benchmark results

`final_200/` contains the submitted experiment outputs for 120 origin-destination pairs and 200 timed runs per algorithm for each pair.

- `final_results_all.csv`: one row per algorithm and route pair
- `final_results_merged.csv`: paired Dijkstra and A* measurements
- `final_results_summary.csv`: overall correctness, timing, and search-efficiency measures
- `final_results_by_haul.csv`: short-, medium-, and long-haul summaries
- `figures/`: charts generated from the saved summary data

Runtime values depend on the machine and operating conditions. Path-cost agreement and node-expansion counts are deterministic for the included graph and algorithm implementations.
