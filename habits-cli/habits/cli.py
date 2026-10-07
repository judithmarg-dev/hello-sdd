import sys
from datetime import date
from pathlib import Path
from habits.core import register_habit, get_records_for_habit, validate_habit_name
from habits.storage import load_registry, save_registry

DEFAULT_DATA_FILE = Path.home() / ".habits" / "registry.json"


def _get_registry(data_file: Path):
    return load_registry(data_file)


def _save(registry, data_file: Path) -> None:
    save_registry(registry, data_file)


def cmd_register(name: str, data_file: Path) -> int:
    """Registra un hábito nuevo o marca uno existente para hoy. (RF-1, RF-4)"""
    if not validate_habit_name(name):
        print(f"Error: nombre inválido '{name}'. Solo letras y números, máximo 100 caracteres.")
        return 1

    registry = _get_registry(data_file)
    today = date.today()
    created = register_habit(registry, name, today)
    _save(registry, data_file)

    habit = registry.habits[name]
    if created:
        print(f"✓ '{name}' registrado. Racha: {habit.streak} día(s).")
    else:
        print(f"'{name}' ya fue registrado hoy. Racha: {habit.streak} día(s).")
    return 0


def cmd_mark(name: str, data_file: Path) -> int:
    """Marca un hábito como cumplido hoy. Alias de register. (RF-4)"""
    return cmd_register(name, data_file)


def cmd_list(data_file: Path) -> int:
    """Lista todos los hábitos con su racha y último registro. (RF-7)"""
    registry = _get_registry(data_file)

    if not registry.habits:
        print("No hay hábitos registrados. Usa 'register <nombre>' para empezar.")
        return 0

    print(f"{'Hábito':<30} {'Racha':>6}  {'Último registro'}")
    print("-" * 55)
    for habit in sorted(registry.habits.values(), key=lambda h: h.name):
        last = habit.last_marked.isoformat() if habit.last_marked else "nunca"
        print(f"{habit.name:<30} {habit.streak:>6}  {last}")
    return 0


def cmd_history(name: str, data_file: Path) -> int:
    """Muestra el histórico de registros de un hábito. (RF-8)"""
    if not validate_habit_name(name):
        print(f"Error: nombre inválido '{name}'.")
        return 1

    registry = _get_registry(data_file)

    if name not in registry.habits:
        print(f"Hábito '{name}' no encontrado.")
        return 1

    records = get_records_for_habit(registry, name)
    if not records:
        print(f"No hay registros para '{name}'.")
        return 0

    print(f"Histórico de '{name}':")
    for record in records:
        print(f"  {record.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    return 0


def run(args: list[str], data_file: Path = DEFAULT_DATA_FILE) -> int:
    if not args:
        print("Uso: habits <comando> [nombre]")
        print("Comandos: register, mark, list, history")
        return 1

    cmd = args[0]

    if cmd in ("register", "mark"):
        if len(args) < 2:
            print(f"Uso: habits {cmd} <nombre>")
            return 1
        name = args[1]
        if cmd == "register":
            return cmd_register(name, data_file)
        return cmd_mark(name, data_file)

    if cmd == "list":
        return cmd_list(data_file)

    if cmd == "history":
        if len(args) < 2:
            print("Uso: habits history <nombre>")
            return 1
        return cmd_history(args[1], data_file)

    print(f"Comando desconocido: '{cmd}'. Comandos válidos: register, mark, list, history")
    return 1
