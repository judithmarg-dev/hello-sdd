import pytest
from datetime import date, datetime
from habits.models import Habit, HabitRecord, Registry


def test_habit_creation():
    habit = Habit(name="Ejercicio", streak=5, last_marked=date(2026, 10, 2))
    assert habit.name == "Ejercicio"
    assert habit.streak == 5
    assert habit.last_marked == date(2026, 10, 2)


def test_habit_record_creation():
    record = HabitRecord(name="Lectura", timestamp=datetime(2026, 10, 2, 8, 30, 0))
    assert record.name == "Lectura"
    assert record.timestamp == datetime(2026, 10, 2, 8, 30, 0)


def test_registry_creation():
    registry = Registry(habits={}, records=[])
    assert registry.habits == {}
    assert registry.records == []


def test_registry_with_habits():
    habit1 = Habit(name="Ejercicio", streak=1, last_marked=date(2026, 10, 2))
    habit2 = Habit(name="Lectura", streak=0, last_marked=None)
    habits_dict = {"Ejercicio": habit1, "Lectura": habit2}

    record1 = HabitRecord(name="Ejercicio", timestamp=datetime(2026, 10, 2, 8, 30, 0))
    records_list = [record1]

    registry = Registry(habits=habits_dict, records=records_list)
    assert len(registry.habits) == 2
    assert len(registry.records) == 1
    assert registry.habits["Ejercicio"].streak == 1
