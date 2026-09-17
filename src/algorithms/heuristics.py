"""
Heuristic utilities for A* search.
"""
from typing import Dict, Tuple
from src.utils.haversine import haversine_km

Coords = Dict[str, Tuple[float, float]]  # IATA -> (lat, lon)

def straight_line_estimate(coords: Coords, a: str, b: str) -> float:
    a = str(a).upper()
    b = str(b).upper()
    if a not in coords or b not in coords:
        return 0.0
    lat1, lon1 = coords[a]
    lat2, lon2 = coords[b]
    return float(haversine_km(lat1, lon1, lat2, lon2))
