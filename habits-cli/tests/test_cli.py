import pytest
import json
import tempfile
from pathlib import Path
from datetime import date, datetime
from habits.cli import run, cmd_register, cmd_mark, cmd_list, cmd_history
from habits.storage import load_registry, save_registry
from habits.models import Registry, Habit, HabitRecord


# ============================================================================
# Helpers
# ============================================================================


def make_registry_file(tmpdir: str, habits: dict = None, records: list = None) -> Path:
    """Crea un archivo JSON de registry en tmpdir con datos iniciales."""
    filepath = Path(tmpdir) / "registry.json"
    registry = Registry(
        habits=habits or {},
        records=records or [],
    )
    save_registry(registry, filepath)
    return filepath


# ============================================================================
# RF-1 + RF-4: register y mark crean el hábito
# ============================================================================


def test_run_register_new_habit(tmp_path, capsys):
    filepath = tmp_path / "registry.json"

    exit_code = run(["register", "Ejercicio"], data_file=filepath)

    assert exit_code == 0
    out = capsys.readouterr().out
    assert "registrado" in out
    assert "Racha: 1" in out

    registry = load_registry(filepath)
    assert "Ejercicio" in registry.habits
    assert registry.habits["Ejercicio"].streak == 1


def test_run_mark_new_habit(tmp_path, capsys):
    filepath = tmp_path / "registry.json"

    exit_code = run(["mark", "Lectura"], data_file=filepath)

    assert exit_code == 0
    registry = load_registry(filepath)
    assert "Lectura" in registry.habits


def test_run_register_missing_name(tmp_path, capsys):
    filepath = tmp_path / "registry.json"

    exit_code = run(["register"], data_file=filepath)

    assert exit_code == 1
    assert "Uso:" in capsys.readouterr().out


def test_run_register_invalid_name(tmp_path, capsys):
    filepath = tmp_path / "registry.json"

    exit_code = run(["register", "Hábito con espacios"], data_file=filepath)

    assert exit_code == 1
    assert "inválido" in capsys.readouterr().out


# ============================================================================
# RF-2: Idempotencia — registrar 2x hoy = 1 registro
# ============================================================================


def test_register_same_habit_twice_same_day_is_idempotent(tmp_path, capsys):
    filepath = tmp_path / "registry.json"

    run(["register", "Ejercicio"], data_file=filepath)
    capsys.readouterr()  # Limpiar salida

    exit_code = run(["register", "Ejercicio"], data_file=filepath)

    assert exit_code == 0
    out = capsys.readouterr().out
    assert "ya fue registrado hoy" in out

    registry = load_registry(filepath)
    ejercicio_records = [r for r in registry.records if r.name == "Ejercicio"]
    assert len(ejercicio_records) == 1


# ============================================================================
# RF-3: Múltiples hábitos distintos el mismo día
# ============================================================================


def test_register_multiple_different_habits(tmp_path):
    filepath = tmp_path / "registry.json"

    run(["register", "Ejercicio"], data_file=filepath)
    run(["register", "Lectura"], data_file=filepath)
    run(["register", "Meditacion"], data_file=filepath)

    registry = load_registry(filepath)
    assert len(registry.habits) == 3
    assert len(registry.records) == 3


# ============================================================================
# RF-7: list muestra todos los hábitos con racha y último registro
# ============================================================================


def test_list_empty_shows_message(tmp_path, capsys):
    filepath = tmp_path / "registry.json"

    exit_code = run(["list"], data_file=filepath)

    assert exit_code == 0
    assert "No hay hábitos" in capsys.readouterr().out


def test_list_shows_habits_with_streak(tmp_path, capsys):
    filepath = tmp_path / "registry.json"
    registry = Registry()
    registry.habits["Ejercicio"] = Habit(
        name="Ejercicio", streak=5, last_marked=date(2026, 10, 7)
    )
    registry.habits["Lectura"] = Habit(
        name="Lectura", streak=2, last_marked=date(2026, 10, 6)
    )
    save_registry(registry, filepath)

    exit_code = run(["list"], data_file=filepath)

    assert exit_code == 0
    out = capsys.readouterr().out
    assert "Ejercicio" in out
    assert "Lectura" in out
    assert "5" in out
    assert "2" in out
    assert "2026-10-07" in out


def test_list_shows_never_for_no_last_marked(tmp_path, capsys):
    filepath = tmp_path / "registry.json"
    registry = Registry()
    registry.habits["Nuevo"] = Habit(name="Nuevo", streak=0, last_marked=None)
    save_registry(registry, filepath)

    run(["list"], data_file=filepath)

    assert "nunca" in capsys.readouterr().out


def test_list_sorted_alphabetically(tmp_path, capsys):
    filepath = tmp_path / "registry.json"
    registry = Registry()
    registry.habits["Yoga"] = Habit(name="Yoga", streak=1, last_marked=date(2026, 10, 7))
    registry.habits["Agua"] = Habit(name="Agua", streak=3, last_marked=date(2026, 10, 7))
    registry.habits["Meditacion"] = Habit(name="Meditacion", streak=2, last_marked=date(2026, 10, 7))
    save_registry(registry, filepath)

    run(["list"], data_file=filepath)

    out = capsys.readouterr().out
    pos_agua = out.index("Agua")
    pos_meditacion = out.index("Meditacion")
    pos_yoga = out.index("Yoga")
    assert pos_agua < pos_meditacion < pos_yoga


# ============================================================================
# RF-8: history muestra fechas cronológicas
# ============================================================================


def test_history_shows_records_in_order(tmp_path, capsys):
    filepath = tmp_path / "registry.json"
    registry = Registry()
    registry.habits["Ejercicio"] = Habit(
        name="Ejercicio", streak=3, last_marked=date(2026, 10, 7)
    )
    registry.records = [
        HabitRecord(name="Ejercicio", timestamp=datetime(2026, 10, 5, 8, 0)),
        HabitRecord(name="Ejercicio", timestamp=datetime(2026, 10, 6, 9, 30)),
        HabitRecord(name="Ejercicio", timestamp=datetime(2026, 10, 7, 7, 15)),
    ]
    save_registry(registry, filepath)

    exit_code = run(["history", "Ejercicio"], data_file=filepath)

    assert exit_code == 0
    out = capsys.readouterr().out
    assert "2026-10-05" in out
    assert "2026-10-06" in out
    assert "2026-10-07" in out
    lines = [l for l in out.splitlines() if "2026" in l]
    assert lines[0] < lines[1] < lines[2]  # orden cronológico


def test_history_habit_not_found(tmp_path, capsys):
    filepath = tmp_path / "registry.json"

    exit_code = run(["history", "Inexistente"], data_file=filepath)

    assert exit_code == 1
    assert "no encontrado" in capsys.readouterr().out


def test_history_invalid_name(tmp_path, capsys):
    filepath = tmp_path / "registry.json"

    exit_code = run(["history", "nombre inválido"], data_file=filepath)

    assert exit_code == 1
    assert "inválido" in capsys.readouterr().out


def test_history_missing_name(tmp_path, capsys):
    filepath = tmp_path / "registry.json"

    exit_code = run(["history"], data_file=filepath)

    assert exit_code == 1
    assert "Uso:" in capsys.readouterr().out


def test_history_only_shows_target_habit(tmp_path, capsys):
    filepath = tmp_path / "registry.json"
    registry = Registry()
    registry.habits["Ejercicio"] = Habit(
        name="Ejercicio", streak=1, last_marked=date(2026, 10, 7)
    )
    registry.habits["Lectura"] = Habit(
        name="Lectura", streak=1, last_marked=date(2026, 10, 7)
    )
    registry.records = [
        HabitRecord(name="Ejercicio", timestamp=datetime(2026, 10, 7, 8, 0)),
        HabitRecord(name="Lectura", timestamp=datetime(2026, 10, 7, 9, 0)),
    ]
    save_registry(registry, filepath)

    run(["history", "Ejercicio"], data_file=filepath)

    out = capsys.readouterr().out
    assert "Ejercicio" in out
    assert "Lectura" not in out


# ============================================================================
# CLI routing: comandos desconocidos y sin argumentos
# ============================================================================


def test_run_no_args(tmp_path, capsys):
    filepath = tmp_path / "registry.json"

    exit_code = run([], data_file=filepath)

    assert exit_code == 1
    assert "Uso:" in capsys.readouterr().out


def test_run_unknown_command(tmp_path, capsys):
    filepath = tmp_path / "registry.json"

    exit_code = run(["desconocido"], data_file=filepath)

    assert exit_code == 1
    assert "desconocido" in capsys.readouterr().out.lower()


# ============================================================================
# RF-10: Persistencia — los datos sobreviven entre llamadas
# ============================================================================


def test_data_persists_between_calls(tmp_path):
    filepath = tmp_path / "registry.json"

    # Primera sesión: registrar
    run(["register", "Ejercicio"], data_file=filepath)

    # Segunda sesión: verificar que persiste
    registry = load_registry(filepath)
    assert "Ejercicio" in registry.habits


def test_streak_persists_across_days(tmp_path):
    filepath = tmp_path / "registry.json"

    # Simular registro en días anteriores
    registry = Registry()
    registry.habits["Ejercicio"] = Habit(
        name="Ejercicio", streak=4, last_marked=date(2026, 10, 6)
    )
    registry.records = [
        HabitRecord(name="Ejercicio", timestamp=datetime(2026, 10, 3, 8, 0)),
        HabitRecord(name="Ejercicio", timestamp=datetime(2026, 10, 4, 8, 0)),
        HabitRecord(name="Ejercicio", timestamp=datetime(2026, 10, 5, 8, 0)),
        HabitRecord(name="Ejercicio", timestamp=datetime(2026, 10, 6, 8, 0)),
    ]
    save_registry(registry, filepath)

    # Verificar que cargó correctamente
    loaded = load_registry(filepath)
    assert loaded.habits["Ejercicio"].streak == 4
    assert len(loaded.records) == 4
