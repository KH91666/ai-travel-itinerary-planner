"""Transparent domain models for the reconstructed itinerary prototype."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time


@dataclass(frozen=True)
class POI:
    id: str
    name: str
    latitude: float
    longitude: float
    open_time: time
    close_time: time
    duration_minutes: int
    priority: int = 1
    area: str = ""
    category: str = ""
    fixed_date: date | None = None
    fixed_time: time | None = None


@dataclass
class ScheduledVisit:
    poi: POI
    day: date
    arrival: time
    departure: time
    locked: bool = False


@dataclass
class DayPlan:
    day: date
    visits: list[ScheduledVisit] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class Itinerary:
    days: list[DayPlan]
    confirmed: bool = False

    @property
    def checks_flagged(self) -> int:
        return sum(len(day.warnings) for day in self.days)
