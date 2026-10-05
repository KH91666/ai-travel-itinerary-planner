"""Load the clearly labelled reconstructed Tokyo demonstration data."""

from __future__ import annotations

import csv
from datetime import date, time
from pathlib import Path

from .models import POI


def _time(value: str) -> time:
    return time.fromisoformat(value)


def load_demo_pois(path: Path | None = None) -> list[POI]:
    path = path or Path(__file__).resolve().parents[1] / "data" / "reconstructed_tokyo_pois.csv"
    pois: list[POI] = []
    with path.open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            pois.append(
                POI(
                    id=row["id"], name=row["name"], latitude=float(row["latitude"]),
                    longitude=float(row["longitude"]), open_time=_time(row["open_time"]),
                    close_time=_time(row["close_time"]), duration_minutes=int(row["duration_minutes"]),
                    priority=int(row["priority"]), area=row["area"], category=row["category"],
                    fixed_date=date.fromisoformat(row["fixed_date"]) if row["fixed_date"] else None,
                    fixed_time=_time(row["fixed_time"]) if row["fixed_time"] else None,
                )
            )
    return pois
