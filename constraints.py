"""Feasibility checks for opening hours, bookings, and daily workload."""

from __future__ import annotations

from datetime import datetime, timedelta

from .models import DayPlan, ScheduledVisit


def add_minutes(value, minutes: int):
    return (datetime.combine(datetime.today(), value) + timedelta(minutes=minutes)).time()


def validate_day(plan: DayPlan, daily_limit_minutes: int = 480) -> list[str]:
    warnings: list[str] = []
    total_minutes = sum(visit.poi.duration_minutes for visit in plan.visits)
    if total_minutes > daily_limit_minutes:
        warnings.append(
            f"Daily workload is {total_minutes} minutes, above the {daily_limit_minutes}-minute limit."
        )
    for visit in plan.visits:
        if visit.arrival < visit.poi.open_time or visit.departure > visit.poi.close_time:
            warnings.append(
                f"{visit.poi.name} falls outside its {visit.poi.open_time:%H:%M}–{visit.poi.close_time:%H:%M} opening window."
            )
        if visit.poi.fixed_date and visit.poi.fixed_date != plan.day:
            warnings.append(f"{visit.poi.name} must remain on {visit.poi.fixed_date.isoformat()}.")
        if visit.poi.fixed_time and visit.arrival != visit.poi.fixed_time:
            warnings.append(f"{visit.poi.name} must start at {visit.poi.fixed_time:%H:%M}.")
    for previous, current in zip(plan.visits, plan.visits[1:]):
        if current.arrival < previous.departure:
            warnings.append(f"{current.poi.name} overlaps with {previous.poi.name}.")
    plan.warnings = warnings
    return warnings


def move_visit(visit: ScheduledVisit, destination: DayPlan) -> None:
    """Move a visit; validation remains an explicit caller responsibility."""
    visit.day = destination.day
    destination.visits.append(visit)
