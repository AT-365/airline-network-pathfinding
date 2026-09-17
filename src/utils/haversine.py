"""
Deterministic Haversine distance calculation in kilometers.

The project uses this one function for both graph edge creation assumptions and
A* straight-line heuristic estimates. Keeping one implementation avoids small
library-to-library differences that could affect the admissibility explanation.
"""
from math import atan2, cos, radians, sin, sqrt
from typing import Union

Number = Union[int, float]
R_EARTH_KM: float = 6371.0


def haversine_km(lat1: Number, lon1: Number, lat2: Number, lon2: Number) -> float:
    """Return great-circle distance between two latitude/longitude points."""
    phi1 = radians(float(lat1))
    phi2 = radians(float(lat2))
    dphi = phi2 - phi1
    dlambda = radians(float(lon2) - float(lon1))

    a = sin(dphi / 2.0) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2.0) ** 2
    c = 2.0 * atan2(sqrt(a), sqrt(1.0 - a))
    return R_EARTH_KM * c
