import json
from pathlib import Path
from datetime import datetime, date
from habits.models import Registry, Habit, HabitRecord


def _serialize_habit(habit: Habit) -> dict:
    """Convert Habit to JSON-serializable dict."""
    return {
        "name": habit.name,
        "streak": habit.streak,
        "last_marked": habit.last_marked.isoformat() if habit.last_marked else None,
    }


def _deserialize_habit(data: dict) -> Habit:
    """Convert dict back to Habit."""
    return Habit(
        name=data["name"],
        streak=data["streak"],
        last_marked=date.fromisoformat(data["last_marked"]) if data["last_marked"] else None,
    )


def _serialize_record(record: HabitRecord) -> dict:
    """Convert HabitRecord to JSON-serializable dict."""
    return {
        "name": record.name,
        "timestamp": record.timestamp.isoformat(),
    }


def _deserialize_record(data: dict) -> HabitRecord:
    """Convert dict back to HabitRecord."""
    return HabitRecord(
        name=data["name"],
        timestamp=datetime.fromisoformat(data["timestamp"]),
    )


def load_registry(filepath: str | Path) -> Registry:
    """
    Carga un Registry desde un archivo JSON.
    Si el archivo no existe, retorna un Registry vacío.
    """
    filepath = Path(filepath)

    if not filepath.exists():
        return Registry()

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    habits = {}
    for habit_data in data.get("habits", []):
        habit = _deserialize_habit(habit_data)
        habits[habit.name] = habit

    records = [_deserialize_record(r) for r in data.get("records", [])]

    return Registry(habits=habits, records=records)


def save_registry(registry: Registry, filepath: str | Path) -> None:
    """
    Guarda un Registry a un archivo JSON.
    Crea el archivo si no existe; sobrescribe si existe.
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "habits": [_serialize_habit(h) for h in registry.habits.values()],
        "records": [_serialize_record(r) for r in registry.records],
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
