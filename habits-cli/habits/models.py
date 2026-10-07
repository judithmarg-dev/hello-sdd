from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class Habit:
    name: str
    streak: int
    last_marked: Optional[date] = None


@dataclass
class HabitRecord:
    name: str
    timestamp: datetime


@dataclass
class Registry:
    habits: dict[str, Habit] = field(default_factory=dict)
    records: list[HabitRecord] = field(default_factory=list)
