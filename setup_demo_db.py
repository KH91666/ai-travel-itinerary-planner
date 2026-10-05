"""Build a small SQLite database containing explicitly simulated demo events."""

from __future__ import annotations

import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "travel_demo.db"


def main() -> None:
    DB.parent.mkdir(exist_ok=True)
    with sqlite3.connect(DB) as connection:
        connection.executescript((ROOT / "sql" / "schema.sql").read_text())
        connection.execute("INSERT INTO users VALUES (1, '2026-09-01T10:00:00')")
        trips = [(1,1,'Tokyo Trip','2026-09-18','2026-09-21','moderate'),
                 (2,1,'Kyoto Trip','2026-10-01','2026-10-03','relaxed'),
                 (3,1,'Osaka Trip','2026-11-01','2026-11-03','moderate')]
        connection.executemany("INSERT INTO trips VALUES (?,?,?,?,?,?)", trips)
        places = [(i, trip, f'Demo place {i}', 'reconstructed demo data', f'2026-09-{10+i:02d}T09:00:00')
                  for i, trip in enumerate([1,1,1,1,1,2,2,2,3], start=1)]
        connection.executemany("INSERT INTO saved_places VALUES (?,?,?,?,?)", places)
        events = [
            (1,1,1,'trip_opened','2026-09-10T09:00:00',None),(2,1,1,'plan_started','2026-09-10T09:05:00',None),
            (3,1,1,'itinerary_generated','2026-09-10T09:06:00',None),(4,1,1,'conflict_detected','2026-09-10T09:07:00','{"poi":"Tsukiji Outer Market"}'),
            (5,1,1,'place_moved','2026-09-10T09:09:00','{"poi":"Akihabara Electric Town"}'),
            (6,1,1,'reoptimized','2026-09-10T09:10:00',None),(7,1,1,'itinerary_confirmed','2026-09-10T09:14:00',None),
            (8,1,2,'trip_opened','2026-09-11T10:00:00',None),(9,1,2,'plan_started','2026-09-11T10:03:00',None),
            (10,1,2,'itinerary_generated','2026-09-11T10:04:00',None),(11,1,2,'itinerary_confirmed','2026-09-11T10:06:00',None),
            (12,1,3,'trip_opened','2026-09-12T11:00:00',None)
        ]
        connection.executemany("INSERT INTO events VALUES (?,?,?,?,?,?)", events)
        connection.execute("INSERT INTO bookings VALUES (1,1,'teamLab Planets','2026-09-20T15:00:00')")
        connection.commit()
    print(f"Created {DB.relative_to(ROOT)} with simulated demo events.")


if __name__ == "__main__":
    main()
