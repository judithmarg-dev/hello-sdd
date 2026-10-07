import pytest
from datetime import date, datetime, timedelta
from habits.core import (
    validate_habit_name,
    register_habit,
    calculate_streak,
    get_records_for_habit,
)
from habits.models import Registry, HabitRecord, Habit


# ============================================================================
# RF-9: Validación de nombres
# ============================================================================


def test_validate_habit_name_valid():
    assert validate_habit_name("Ejercicio") is True
    assert validate_habit_name("Lectura123") is True
    assert validate_habit_name("A") is True
    assert validate_habit_name("Z9z") is True


def test_validate_habit_name_empty():
    assert validate_habit_name("") is False


def test_validate_habit_name_with_spaces():
    assert validate_habit_name("Ejercicio matutino") is False
    assert validate_habit_name("Leer libros") is False


def test_validate_habit_name_with_special_chars():
    assert validate_habit_name("Ejercicio!") is False
    assert validate_habit_name("Lectura-123") is False
    assert validate_habit_name("Hábito@") is False
    assert validate_habit_name("Yoga (mañana)") is False


def test_validate_habit_name_max_length():
    # 100 caracteres alfanuméricos válido
    assert validate_habit_name("A" * 100) is True
    # 101 caracteres inválido
    assert validate_habit_name("A" * 101) is False


def test_validate_habit_name_unicode():
    # No alfanuméricos ASCII
    assert validate_habit_name("Élite") is False
    assert validate_habit_name("日本語") is False


# ============================================================================
# RF-1: Registrar hábito
# ============================================================================


def test_register_habit_creates_new_habit():
    """Registrar un nuevo hábito lo persiste con streak=1."""
    registry = Registry()
    today = date(2026, 10, 7)

    result = register_habit(registry, "Ejercicio", today)

    assert result is True
    assert "Ejercicio" in registry.habits
    assert registry.habits["Ejercicio"].streak == 1
    assert registry.habits["Ejercicio"].last_marked == today


def test_register_habit_creates_record():
    """Registrar un hábito crea un HabitRecord."""
    registry = Registry()
    today = date(2026, 10, 7)

    register_habit(registry, "Lectura", today)

    assert len(registry.records) == 1
    assert registry.records[0].name == "Lectura"
    assert registry.records[0].timestamp.date() == today


def test_register_habit_invalid_name_raises():
    """Registrar con nombre inválido lanza error."""
    registry = Registry()
    today = date(2026, 10, 7)

    with pytest.raises(ValueError):
        register_habit(registry, "Ejercicio!", today)

    with pytest.raises(ValueError):
        register_habit(registry, "", today)


# ============================================================================
# RF-2: Idempotencia de registro
# ============================================================================


def test_register_same_habit_same_day_idempotent():
    """Registrar el mismo hábito 2x el mismo día ignora el segundo (idempotencia)."""
    registry = Registry()
    today = date(2026, 10, 7)

    result1 = register_habit(registry, "Ejercicio", today)
    result2 = register_habit(registry, "Ejercicio", today)

    assert result1 is True  # Primera vez registra
    assert result2 is False  # Segunda vez ignora

    # Solo un registro en la lista
    ejercicio_records = [r for r in registry.records if r.name == "Ejercicio"]
    assert len(ejercicio_records) == 1

    # Streak sigue siendo 1
    assert registry.habits["Ejercicio"].streak == 1


# ============================================================================
# RF-3: Múltiples hábitos por día
# ============================================================================


def test_register_different_habits_same_day():
    """Registrar 2 hábitos diferentes el mismo día ambos se guardan."""
    registry = Registry()
    today = date(2026, 10, 7)

    result1 = register_habit(registry, "Ejercicio", today)
    result2 = register_habit(registry, "Lectura", today)

    assert result1 is True
    assert result2 is True

    assert len(registry.habits) == 2
    assert len(registry.records) == 2
    assert "Ejercicio" in registry.habits
    assert "Lectura" in registry.habits


# ============================================================================
# RF-5: Calcular racha consecutiva
# ============================================================================


def test_calculate_streak_empty_records():
    """Racha vacía = 0."""
    today = date(2026, 10, 7)
    assert calculate_streak([], today) == 0


def test_calculate_streak_single_day_today():
    """Un registro hoy = racha de 1."""
    today = date(2026, 10, 7)
    records = [HabitRecord(name="Test", timestamp=datetime(2026, 10, 7, 8, 0))]

    assert calculate_streak(records, today) == 1


def test_calculate_streak_single_day_yesterday():
    """Un registro ayer = racha de 1 (ayer está dentro del rango)."""
    today = date(2026, 10, 7)
    yesterday = date(2026, 10, 6)
    records = [HabitRecord(name="Test", timestamp=datetime(2026, 10, 6, 8, 0))]

    assert calculate_streak(records, today) == 1


def test_calculate_streak_gap_two_days():
    """Último registro hace 2+ días = racha 0."""
    today = date(2026, 10, 7)
    two_days_ago = date(2026, 10, 5)
    records = [HabitRecord(name="Test", timestamp=datetime(2026, 10, 5, 8, 0))]

    assert calculate_streak(records, today) == 0


def test_calculate_streak_consecutive_3_days():
    """Registros en 3 días consecutivos = racha 3."""
    today = date(2026, 10, 7)
    records = [
        HabitRecord(name="Test", timestamp=datetime(2026, 10, 5, 8, 0)),
        HabitRecord(name="Test", timestamp=datetime(2026, 10, 6, 10, 0)),
        HabitRecord(name="Test", timestamp=datetime(2026, 10, 7, 9, 0)),
    ]

    assert calculate_streak(records, today) == 3


def test_calculate_streak_with_gap_in_middle():
    """Registros con gap en el medio: racha cuenta desde el final hacia atrás."""
    today = date(2026, 10, 7)
    records = [
        HabitRecord(name="Test", timestamp=datetime(2026, 10, 2, 8, 0)),
        HabitRecord(name="Test", timestamp=datetime(2026, 10, 3, 8, 0)),
        # GAP: 10-04 y 10-05 sin registro
        HabitRecord(name="Test", timestamp=datetime(2026, 10, 6, 8, 0)),
        HabitRecord(name="Test", timestamp=datetime(2026, 10, 7, 8, 0)),
    ]

    # Racha = últimos 2 días consecutivos
    assert calculate_streak(records, today) == 2


def test_calculate_streak_multiple_entries_same_day():
    """Múltiples registros el mismo día cuentan como 1 día."""
    today = date(2026, 10, 7)
    records = [
        HabitRecord(name="Test", timestamp=datetime(2026, 10, 7, 8, 0)),
        HabitRecord(name="Test", timestamp=datetime(2026, 10, 7, 12, 0)),
        HabitRecord(name="Test", timestamp=datetime(2026, 10, 7, 18, 0)),
    ]

    assert calculate_streak(records, today) == 1


# ============================================================================
# RF-6: Reinicio de racha por hueco
# ============================================================================


def test_streak_breaks_after_gap():
    """Racha se reinicia después de >24h sin registro."""
    today = date(2026, 10, 10)
    records = [
        HabitRecord(name="Test", timestamp=datetime(2026, 10, 5, 8, 0)),
        HabitRecord(name="Test", timestamp=datetime(2026, 10, 6, 8, 0)),
        # GAP: 10-07, 10-08, 10-09 sin registro (>24h)
        HabitRecord(name="Test", timestamp=datetime(2026, 10, 10, 8, 0)),
    ]

    # La racha actual empieza hoy, sin conexión con los días anteriores
    assert calculate_streak(records, today) == 1


def test_register_after_gap_resets_streak():
    """Registrar después de un hueco reinicia la racha a 1."""
    registry = Registry()
    day1 = date(2026, 10, 5)
    day2 = date(2026, 10, 6)
    day_gap = date(2026, 10, 10)  # 3+ días después

    # Registrar 2 días seguidos
    register_habit(registry, "Ejercicio", day1)
    register_habit(registry, "Ejercicio", day2)
    assert registry.habits["Ejercicio"].streak == 2

    # Registrar después del gap
    register_habit(registry, "Ejercicio", day_gap)

    # Racha vuelve a 1
    assert registry.habits["Ejercicio"].streak == 1


# ============================================================================
# Helpers
# ============================================================================


def test_get_records_for_habit():
    """get_records_for_habit retorna registros en orden cronológico."""
    registry = Registry()
    registry.records = [
        HabitRecord(name="Ejercicio", timestamp=datetime(2026, 10, 5, 8, 0)),
        HabitRecord(name="Lectura", timestamp=datetime(2026, 10, 6, 8, 0)),
        HabitRecord(name="Ejercicio", timestamp=datetime(2026, 10, 7, 8, 0)),
    ]

    ejercicio_records = get_records_for_habit(registry, "Ejercicio")

    assert len(ejercicio_records) == 2
    assert ejercicio_records[0].timestamp.date() == date(2026, 10, 5)
    assert ejercicio_records[1].timestamp.date() == date(2026, 10, 7)
