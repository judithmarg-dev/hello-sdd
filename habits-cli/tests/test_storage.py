import pytest
import json
import tempfile
from pathlib import Path
from datetime import date, datetime
from habits.storage import load_registry, save_registry
from habits.models import Registry, Habit, HabitRecord


# ============================================================================
# RF-10: Persistencia JSON - Load/Save Operations
# ============================================================================


def test_load_nonexistent_file_returns_empty_registry():
    """Cargar de archivo inexistente retorna Registry vacío."""
    with tempfile.TemporaryDirectory() as tmpdir:
        nonexistent = Path(tmpdir) / "nonexistent.json"

        registry = load_registry(nonexistent)

        assert isinstance(registry, Registry)
        assert len(registry.habits) == 0
        assert len(registry.records) == 0


def test_load_empty_registry_from_file():
    """Cargar un archivo JSON vacío retorna Registry vacío."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "empty.json"
        filepath.write_text(json.dumps({"habits": [], "records": []}))

        registry = load_registry(filepath)

        assert len(registry.habits) == 0
        assert len(registry.records) == 0


def test_save_empty_registry_creates_file():
    """Guardar un Registry vacío crea el archivo."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "empty.json"

        registry = Registry()
        save_registry(registry, filepath)

        assert filepath.exists()
        data = json.loads(filepath.read_text())
        assert data == {"habits": [], "records": []}


def test_save_and_load_single_habit():
    """Guardar y cargar un solo hábito preserva datos."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "single.json"

        # Crear y guardar
        original = Registry()
        original.habits["Ejercicio"] = Habit(
            name="Ejercicio", streak=5, last_marked=date(2026, 10, 7)
        )

        save_registry(original, filepath)

        # Cargar y verificar
        loaded = load_registry(filepath)

        assert len(loaded.habits) == 1
        assert "Ejercicio" in loaded.habits
        assert loaded.habits["Ejercicio"].streak == 5
        assert loaded.habits["Ejercicio"].last_marked == date(2026, 10, 7)


def test_save_and_load_single_record():
    """Guardar y cargar un solo registro preserva datos."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "record.json"

        # Crear y guardar
        original = Registry()
        original.records.append(
            HabitRecord(name="Lectura", timestamp=datetime(2026, 10, 7, 8, 30, 45))
        )

        save_registry(original, filepath)

        # Cargar y verificar
        loaded = load_registry(filepath)

        assert len(loaded.records) == 1
        assert loaded.records[0].name == "Lectura"
        assert loaded.records[0].timestamp == datetime(2026, 10, 7, 8, 30, 45)


def test_save_and_load_multiple_habits():
    """Guardar y cargar múltiples hábitos."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "multi.json"

        # Crear y guardar
        original = Registry()
        original.habits["Ejercicio"] = Habit(
            name="Ejercicio", streak=3, last_marked=date(2026, 10, 7)
        )
        original.habits["Lectura"] = Habit(
            name="Lectura", streak=7, last_marked=date(2026, 10, 5)
        )
        original.habits["Meditacion"] = Habit(
            name="Meditacion", streak=0, last_marked=None
        )

        save_registry(original, filepath)

        # Cargar y verificar
        loaded = load_registry(filepath)

        assert len(loaded.habits) == 3
        assert loaded.habits["Ejercicio"].streak == 3
        assert loaded.habits["Lectura"].streak == 7
        assert loaded.habits["Meditacion"].streak == 0
        assert loaded.habits["Meditacion"].last_marked is None


def test_save_and_load_multiple_records():
    """Guardar y cargar múltiples registros."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "records.json"

        # Crear y guardar
        original = Registry()
        original.records.append(
            HabitRecord(name="Ejercicio", timestamp=datetime(2026, 10, 5, 8, 0))
        )
        original.records.append(
            HabitRecord(name="Lectura", timestamp=datetime(2026, 10, 6, 10, 30))
        )
        original.records.append(
            HabitRecord(name="Ejercicio", timestamp=datetime(2026, 10, 7, 9, 15))
        )

        save_registry(original, filepath)

        # Cargar y verificar
        loaded = load_registry(filepath)

        assert len(loaded.records) == 3
        assert loaded.records[0].name == "Ejercicio"
        assert loaded.records[1].name == "Lectura"
        assert loaded.records[2].name == "Ejercicio"


def test_save_and_load_complex_registry():
    """Guardar y cargar un Registry complejo con múltiples hábitos y registros."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "complex.json"

        # Crear un registry complejo
        original = Registry()

        # Hábitos
        original.habits["Ejercicio"] = Habit(
            name="Ejercicio", streak=10, last_marked=date(2026, 10, 7)
        )
        original.habits["Lectura"] = Habit(
            name="Lectura", streak=5, last_marked=date(2026, 10, 6)
        )
        original.habits["Meditacion"] = Habit(
            name="Meditacion", streak=1, last_marked=date(2026, 10, 7)
        )

        # Registros
        original.records = [
            HabitRecord(name="Ejercicio", timestamp=datetime(2026, 9, 28, 7, 0)),
            HabitRecord(name="Ejercicio", timestamp=datetime(2026, 9, 29, 7, 0)),
            HabitRecord(name="Lectura", timestamp=datetime(2026, 10, 2, 19, 30)),
            HabitRecord(name="Ejercicio", timestamp=datetime(2026, 10, 3, 8, 0)),
            HabitRecord(name="Meditacion", timestamp=datetime(2026, 10, 7, 6, 0)),
            HabitRecord(name="Ejercicio", timestamp=datetime(2026, 10, 7, 8, 0)),
        ]

        save_registry(original, filepath)
        loaded = load_registry(filepath)

        # Verificar hábitos
        assert len(loaded.habits) == 3
        assert loaded.habits["Ejercicio"].streak == 10
        assert loaded.habits["Lectura"].streak == 5
        assert loaded.habits["Meditacion"].streak == 1

        # Verificar registros
        assert len(loaded.records) == 6
        assert loaded.records[2].name == "Lectura"
        assert loaded.records[2].timestamp == datetime(2026, 10, 2, 19, 30)


def test_save_creates_parent_directories():
    """Guardar crea directorios padre si no existen."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "subdir" / "nested" / "registry.json"

        registry = Registry()
        save_registry(registry, filepath)

        assert filepath.exists()
        assert filepath.parent.exists()


# ============================================================================
# Data Integrity & Format Tests
# ============================================================================


def test_json_format_is_valid():
    """El archivo JSON guardado debe ser válido."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "valid.json"

        original = Registry()
        original.habits["Test"] = Habit(name="Test", streak=1, last_marked=date(2026, 10, 7))
        original.records.append(
            HabitRecord(name="Test", timestamp=datetime(2026, 10, 7, 8, 0))
        )

        save_registry(original, filepath)

        # Verificar que es JSON válido
        with open(filepath) as f:
            data = json.load(f)

        assert "habits" in data
        assert "records" in data
        assert isinstance(data["habits"], list)
        assert isinstance(data["records"], list)


def test_json_contains_expected_fields():
    """El JSON debe contener los campos esperados."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "fields.json"

        original = Registry()
        original.habits["Ejercicio"] = Habit(
            name="Ejercicio", streak=5, last_marked=date(2026, 10, 7)
        )

        save_registry(original, filepath)

        with open(filepath) as f:
            data = json.load(f)

        habit = data["habits"][0]
        assert "name" in habit
        assert "streak" in habit
        assert "last_marked" in habit


def test_load_preserves_none_last_marked():
    """Cargar un hábito con last_marked=None preserva el None."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "none.json"

        original = Registry()
        original.habits["Nuevo"] = Habit(name="Nuevo", streak=0, last_marked=None)

        save_registry(original, filepath)
        loaded = load_registry(filepath)

        assert loaded.habits["Nuevo"].last_marked is None


def test_iso_format_datetime_precision():
    """Los timestamps se preservan con precisión ISO."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "precision.json"

        original = Registry()
        ts = datetime(2026, 10, 7, 8, 30, 45, 123456)
        original.records.append(HabitRecord(name="Test", timestamp=ts))

        save_registry(original, filepath)
        loaded = load_registry(filepath)

        # ISO format preserva microseconds
        assert loaded.records[0].timestamp == ts


def test_unicode_habit_names_in_json():
    """Los nombres de hábitos se guardan y cargan correctamente."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "unicode.json"

        original = Registry()
        original.habits["Exercice"] = Habit(
            name="Exercice", streak=2, last_marked=date(2026, 10, 7)
        )

        save_registry(original, filepath)
        loaded = load_registry(filepath)

        assert "Exercice" in loaded.habits
        assert loaded.habits["Exercice"].name == "Exercice"


# ============================================================================
# Edge Cases & Error Handling
# ============================================================================


def test_load_from_string_path():
    """load_registry acepta string como filepath."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath_str = str(Path(tmpdir) / "test.json")

        original = Registry()
        original.habits["Test"] = Habit(
            name="Test", streak=1, last_marked=date(2026, 10, 7)
        )

        save_registry(original, filepath_str)
        loaded = load_registry(filepath_str)

        assert "Test" in loaded.habits


def test_save_overwrites_existing_file():
    """Guardar sobrescribe un archivo existente."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "overwrite.json"

        # Guardar primero
        registry1 = Registry()
        registry1.habits["Old"] = Habit(name="Old", streak=99, last_marked=None)
        save_registry(registry1, filepath)

        # Guardar de nuevo con datos diferentes
        registry2 = Registry()
        registry2.habits["New"] = Habit(name="New", streak=1, last_marked=date(2026, 10, 7))
        save_registry(registry2, filepath)

        # Cargar y verificar
        loaded = load_registry(filepath)
        assert "Old" not in loaded.habits
        assert "New" in loaded.habits


def test_empty_habits_dict_loads_as_empty():
    """Un dict de habits vacío se carga como dict vacío."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "empty_habits.json"

        registry = Registry()
        registry.records.append(
            HabitRecord(name="Test", timestamp=datetime(2026, 10, 7, 8, 0))
        )

        save_registry(registry, filepath)
        loaded = load_registry(filepath)

        assert len(loaded.habits) == 0
        assert len(loaded.records) == 1


def test_empty_records_list_loads_as_empty():
    """Una lista de records vacía se carga como lista vacía."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "empty_records.json"

        registry = Registry()
        registry.habits["Test"] = Habit(name="Test", streak=1, last_marked=None)

        save_registry(registry, filepath)
        loaded = load_registry(filepath)

        assert len(loaded.habits) == 1
        assert len(loaded.records) == 0


def test_roundtrip_preserves_order():
    """Un roundtrip save/load preserva el orden de los registros."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "order.json"

        original = Registry()
        for i in range(5):
            original.records.append(
                HabitRecord(
                    name=f"Habit{i}",
                    timestamp=datetime(2026, 10, 1 + i, 8, 0),
                )
            )

        save_registry(original, filepath)
        loaded = load_registry(filepath)

        assert len(loaded.records) == 5
        for i in range(5):
            assert loaded.records[i].name == f"Habit{i}"
            assert loaded.records[i].timestamp.day == 1 + i
