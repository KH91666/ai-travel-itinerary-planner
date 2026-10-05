"""Geographic utilities. The routing heuristic is intentionally simple."""

from __future__ import annotations

from math import asin, cos, radians, sin, sqrt

from .models import POI


def haversine_km(a: POI, b: POI) -> float:
    """Return great-circle distance between two POIs in kilometres."""
    earth_radius_km = 6371.0088
    d_lat = radians(b.latitude - a.latitude)
    d_lon = radians(b.longitude - a.longitude)
    lat_a, lat_b = radians(a.latitude), radians(b.latitude)
    h = sin(d_lat / 2) ** 2 + cos(lat_a) * cos(lat_b) * sin(d_lon / 2) ** 2
    return 2 * earth_radius_km * asin(sqrt(h))


def nearest_neighbour(pois: list[POI], start: POI | None = None) -> list[POI]:
    """Order POIs with a nearest-neighbour heuristic, preserving fixed visits."""
    if not pois:
        return []
    remaining = list(pois)
    current = start or max(remaining, key=lambda poi: poi.priority)
    if current in remaining:
        remaining.remove(current)
    ordered = [current]
    while remaining:
        current = min(remaining, key=lambda poi: haversine_km(ordered[-1], poi))
        remaining.remove(current)
        ordered.append(current)
    return ordered


def group_by_area(pois: list[POI]) -> dict[str, list[POI]]:
    """Use supplied area labels as explainable geographic clusters."""
    groups: dict[str, list[POI]] = {}
    for poi in pois:
        groups.setdefault(poi.area or "Other", []).append(poi)
    return groups
