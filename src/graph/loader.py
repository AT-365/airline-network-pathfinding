"""
Plain-Python graph loader for nodes.csv and edges.csv.

Expected headers:
- nodes.csv: iata, lat, lon
- edges.csv: src, dst, distance_km
"""
from typing import Dict, List, Tuple
import csv

Adj = Dict[str, List[Tuple[str, float]]]
Coords = Dict[str, Tuple[float, float]]

def load_graph(nodes_file: str, edges_file: str) -> Tuple[Adj, Coords]:
    coords: Coords = {}
    with open(nodes_file, newline="", encoding="utf-8") as nf:
        reader = csv.DictReader(nf)
        for row in reader:
            iata = str(row["iata"]).strip().upper()
            lat = float(row["lat"])
            lon = float(row["lon"])
            coords[iata] = (lat, lon)

    adj: Adj = {}
    with open(edges_file, newline="", encoding="utf-8") as ef:
        reader = csv.DictReader(ef)
        for row in reader:
            src = str(row["src"]).strip().upper()
            dst = str(row["dst"]).strip().upper()
            w = float(row["distance_km"])
            adj.setdefault(src, []).append((dst, w))

    return adj, coords
