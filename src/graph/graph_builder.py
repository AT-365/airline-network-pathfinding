"""
Optional graph visualization script for the CSCI 7432 airline network project.

This script reads the CSV files in the project's data directory, builds a
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
NODES_CSV = PROJECT_ROOT / "data" / "nodes.csv"
EDGES_CSV = PROJECT_ROOT / "data" / "edges.csv"
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

    fig, ax = plt.subplots(figsize=(14, 10))
    nx.draw_networkx_nodes(
        graph,
        positions,
        node_size=520,
        node_color="#7dd3fc",
        edgecolors="#0f172a",
        linewidths=0.8,
        ax=ax,
    )
    nx.draw_networkx_edges(
        graph,
        positions,
        alpha=0.22,
        width=0.8,
        arrows=True,
        arrowsize=7,
        connectionstyle="arc3,rad=0.02",
        ax=ax,
    )

    # Offset labels in the two densest metro clusters so every airport code is legible.
    label_offsets = {
        "EWR": (-18, 10),
        "JFK": (18, 2),
        "FLL": (-24, 10),
        "MIA": (24, -9),
    }
    for airport, (x, y) in positions.items():
        dx, dy = label_offsets.get(airport, (0, 0))
        ax.annotate(
            airport,
            xy=(x, y),
            xytext=(dx, dy),
            textcoords="offset points",
            ha="center",
            va="center",
            fontsize=8.5,
            fontweight="bold",
            color="#0f172a",
            bbox=(
                {"boxstyle": "round,pad=0.12", "facecolor": "white", "edgecolor": "none", "alpha": 0.82}
                if airport in label_offsets
                else None
            ),
        )

    ax.set_title("Directed Airline Route Graph for 20-Airport Sample", fontsize=16, pad=16)
    ax.axis("off")
    fig.tight_layout()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PATH, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved graph visualization to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
