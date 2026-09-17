"""
Optional graph visualization script for the CSCI 7432 airline network project.

This script reads the project-level nodes.csv and edges.csv files, builds a
NetworkX directed graph, and saves a high-resolution visualization. It is not
required to reproduce the benchmark results; the official experiment command is:

    python tools/run_final_experiment.py --runs 200 --outdir results/final_200
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
NODES_CSV = PROJECT_ROOT / "nodes.csv"
EDGES_CSV = PROJECT_ROOT / "edges.csv"
OUTPUT_PATH = PROJECT_ROOT / "results" / "final_200" / "figures" / "hub_spoke_airline_graph.png"


def main() -> None:
    nodes_df = pd.read_csv(NODES_CSV)
    edges_df = pd.read_csv(EDGES_CSV)

    graph = nx.DiGraph()
    positions = {row["iata"]: (row["lon"], row["lat"]) for _, row in nodes_df.iterrows()}

    for _, row in nodes_df.iterrows():
        graph.add_node(row["iata"])

    for _, row in edges_df.iterrows():
        graph.add_edge(row["src"], row["dst"], weight=float(row["distance_km"]))

    plt.figure(figsize=(14, 10))
    nx.draw_networkx_nodes(graph, positions, node_size=600, node_color="skyblue")
    nx.draw_networkx_edges(graph, positions, alpha=0.4, width=1)
    nx.draw_networkx_labels(graph, positions, font_size=9, font_weight="bold")
    plt.title("Directed Airline Route Graph for 20-Airport Sample", fontsize=16)
    plt.axis("off")
    plt.tight_layout()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUTPUT_PATH, dpi=300)
    plt.close()
    print(f"Saved graph visualization to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
