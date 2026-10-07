import re
from datetime import date, datetime, timedelta
from habits.models import Habit, HabitRecord, Registry


def validate_habit_name(name: str) -> bool:
    """
    Valida que un nombre de hábito sea alfanumérico ASCII, 1-100 caracteres.
    Retorna True si es válido, False de lo contrario.
    """
    if not name or len(name) == 0 or len(name) > 100:
        return False
    return bool(re.match(r"^[a-zA-Z0-9]+$", name))


def get_records_for_habit(registry: Registry, habit_name: str) -> list[HabitRecord]:
    """Retorna todos los registros para un hábito específico, ordenados por timestamp."""
    return sorted(
        [r for r in registry.records if r.name == habit_name],
        key=lambda r: r.timestamp,
    )


def calculate_streak(
    records: list[HabitRecord], today: date
) -> int:
    """
    Calcula la racha consecutiva de días para un hábito.

    Racha = contador de días consecutivos desde hoy hacia atrás sin gaps.
    Un gap = más de 24h sin registro (es decir, un día completo sin marcar).
    """
    if not records:
        return 0

    sorted_records = sorted(records, key=lambda r: r.timestamp)
    last_record = sorted_records[-1]
    last_date = last_record.timestamp.date()

    # Si el último registro es de hace 2+ días, racha es 0
    days_ago = (today - last_date).days
    if days_ago > 1:
        return 0

    # Racha = 1 si marcó hoy o ayer, luego buscar hacia atrás
    streak = 1
    current_check_date = last_date - timedelta(days=1)

    for i in range(len(sorted_records) - 2, -1, -1):
        record_date = sorted_records[i].timestamp.date()

        if record_date == current_check_date:
            streak += 1
            current_check_date -= timedelta(days=1)
        elif record_date < current_check_date:
            # Gap encontrado, detenerse
            break

    return streak


def register_habit(registry: Registry, name: str, today: date) -> bool:
    """
    Registra un hábito para hoy (RF-1, RF-2, RF-3).

    Retorna True si el registro fue nuevo, False si ya existía hoy (idempotencia).
    - Si no existe, crea con streak=1
    - Si ya existe hoy, ignora (idempotencia)
    - Permite múltiples hábitos diferentes el mismo día
    """
    if not validate_habit_name(name):
        raise ValueError(f"Nombre de hábito inválido: {name}")

    # Verificar si ya fue registrado hoy (idempotencia)
    today_records = [r for r in registry.records if r.name == name and r.timestamp.date() == today]
    if today_records:
        return False  # Ya registrado hoy

    # Crear/obtener hábito
    if name not in registry.habits:
        registry.habits[name] = Habit(name=name, streak=0, last_marked=None)

    # Registrar hoy
    registry.records.append(HabitRecord(name=name, timestamp=datetime.combine(today, datetime.min.time())))

    # Recalcular racha
    records = get_records_for_habit(registry, name)
    streak = calculate_streak(records, today)
    registry.habits[name].streak = streak
    registry.habits[name].last_marked = today

    return True
