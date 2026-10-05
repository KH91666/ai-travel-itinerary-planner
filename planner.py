"""Deterministic day allocation, sequencing, scheduling, and validation."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta

from .constraints import validate_day
from .models import DayPlan, Itinerary, POI, ScheduledVisit
from .routing import group_by_area, nearest_neighbour


PACE_LIMITS = {"relaxed": 360, "moderate": 480, "busy": 600}


def _add_minutes(value: time, minutes: int) -> time:
    return (datetime.combine(date.today(), value) + timedelta(minutes=minutes)).time()


def allocate_days(pois: list[POI], trip_days: list[date]) -> dict[date, list[POI]]:
    """Allocate fixed bookings first, then whole geographic groups by load."""
    allocation = {day: [] for day in trip_days}
    fixed_ids: set[str] = set()
    for poi in pois:
        if poi.fixed_date in allocation:
            allocation[poi.fixed_date].append(poi)
            fixed_ids.add(poi.id)

    groups = group_by_area([poi for poi in pois if poi.id not in fixed_ids])
    for _, group in sorted(groups.items(), key=lambda item: -sum(p.priority for p in item[1])):
        day = min(
            trip_days,
            key=lambda d: sum(p.duration_minutes for p in allocation[d]),
        )
        allocation[day].extend(sorted(group, key=lambda poi: -poi.priority))
    return allocation


def schedule_day(day: date, pois: list[POI], start_at: time = time(9, 0)) -> DayPlan:
    """Build a readable schedule around any fixed-time booking."""
    fixed = [poi for poi in pois if poi.fixed_time]
    flexible = nearest_neighbour([poi for poi in pois if not poi.fixed_time])
    ordered = flexible + fixed
    visits: list[ScheduledVisit] = []
    cursor = start_at
    for poi in ordered:
        arrival = poi.fixed_time or max(cursor, poi.open_time)
        departure = _add_minutes(arrival, poi.duration_minutes)
        visits.append(
            ScheduledVisit(
                poi=poi,
                day=day,
                arrival=arrival,
                departure=departure,
                locked=bool(poi.fixed_time),
            )
        )
        cursor = _add_minutes(departure, 30)
    visits.sort(key=lambda visit: visit.arrival)
    return DayPlan(day=day, visits=visits)


def build_itinerary(pois: list[POI], trip_days: list[date], pace: str = "moderate") -> Itinerary:
    limit = PACE_LIMITS[pace]
    allocation = allocate_days(pois, trip_days)
    days = [schedule_day(day, allocation[day]) for day in trip_days]
    for day in days:
        validate_day(day, daily_limit_minutes=limit)
    return Itinerary(days=days)


def confirm_itinerary(itinerary: Itinerary) -> bool:
    if itinerary.checks_flagged:
        return False
    itinerary.confirmed = True
    return True
