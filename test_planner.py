from datetime import date, time
import sqlite3
import subprocess
import sys
import unittest
from pathlib import Path

from src.constraints import validate_day
from src.demo_data import load_demo_pois
from src.models import DayPlan, ScheduledVisit
from src.planner import build_itinerary, confirm_itinerary
from src.routing import haversine_km


ROOT = Path(__file__).resolve().parents[1]


class PlannerTests(unittest.TestCase):
    def setUp(self):
        self.pois = load_demo_pois()
        self.by_id = {poi.id: poi for poi in self.pois}

    def test_haversine_distance(self):
        distance = haversine_km(self.by_id["tsukiji"], self.by_id["teamlab"])
        self.assertGreater(distance, 1)
        self.assertLess(distance, 5)

    def test_fixed_booking_preserved(self):
        days = [date(2026, 9, 18), date(2026, 9, 19), date(2026, 9, 20), date(2026, 9, 21)]
        itinerary = build_itinerary(self.pois, days)
        visit = next(v for d in itinerary.days for v in d.visits if v.poi.id == "teamlab")
        self.assertEqual(visit.day, date(2026, 9, 20))
        self.assertEqual(visit.arrival, time(15, 0))

    def test_opening_hour_conflict(self):
        poi = self.by_id["tsukiji"]
        visit = ScheduledVisit(poi, date(2026, 9, 18), time(14, 0), time(15, 30))
        day = DayPlan(visit.day, [visit])
        self.assertTrue(any("opening window" in w for w in validate_day(day)))

    def test_confirmation_requires_no_warnings(self):
        itinerary = build_itinerary([self.by_id["teamlab"]], [date(2026, 9, 20)])
        self.assertTrue(confirm_itinerary(itinerary))

    def test_event_kpi_sql_sanity(self):
        subprocess.run([sys.executable, str(ROOT / "scripts" / "setup_demo_db.py")], check=True)
        with sqlite3.connect(ROOT / "data" / "travel_demo.db") as con:
            conversion = con.execute("""SELECT 1.0*COUNT(DISTINCT CASE WHEN event_name='plan_started' THEN trip_id END)/COUNT(DISTINCT CASE WHEN event_name='trip_opened' THEN trip_id END) FROM events""").fetchone()[0]
            self.assertAlmostEqual(conversion, 2/3)


if __name__ == "__main__":
    unittest.main()
