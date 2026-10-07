# Tasks: Habits MVP

**Plan de trabajo** — tareas ≤30 min, ordenadas por dependencia.

---

## FASE 1: Tipos Base

### ☑ T1: Definir models.py
**Dependencia**: Ninguna  
**RF**: Base para todos  
**Duración**: ~15 min  
**Hecho cuando**:
- `models.py` contiene dataclasses: `Habit`, `HabitRecord`, `Registry`
- Todas tienen type hints completos (PEP 484)
- `python -c "from habits.models import *"` no lanza ImportError

---

## FASE 2: Lógica Core (Puro)

### ☑ T2: core.validate_habit_name()
**Dependencia**: T1 (models)  
**RF**: RF-9  
**Duración**: ~10 min  
**Hecho cuando**:
- Función retorna `True` si nombre es alfanumérico, 1-100 chars
- Retorna `False` si vacío, con espacios, o caracteres especiales
- `pytest -q tests/test_core.py::test_validate_habit_name` pasa 100%

### ☑ T3: core.register_habit()
**Dependencia**: T2 (validate)  
**RF**: RF-1, RF-2, RF-3  
**Duración**: ~15 min  
**Hecho cuando**:
- Crea `Habit` nuevo con `streak=0`, `last_marked=None`
- Inserta en `registry.habits[name]` solo si no existe
- 2x register mismo nombre = idempotencia (no error)
- `pytest -q tests/test_core.py::test_register_habit` pasa

### ☑ T4: core.mark_habit() — parte 1: Sin hueco
**Dependencia**: T3 (register)  
**RF**: RF-2, RF-4, RF-5  
**Duración**: ~20 min  
**Hecho cuando**:
- Incrementa `streak` si no hay hueco (consecutivos)
- Actualiza `last_marked = today`
- 2x mark hoy = idempotencia (streak no se dobla)
- Agrega `HabitRecord(name, timestamp)` a `registry.records`
- `pytest -q tests/test_core.py::test_mark_habit_no_gap` pasa

### ☑ T5: core.mark_habit() — parte 2: Detección de hueco
**Dependencia**: T4 (mark sin hueco)  
**RF**: RF-6  
**Duración**: ~15 min  
**Hecho cuando**:
- Si `today > last_marked + 1 día` → resetea `streak = 0` antes de incrementar
- Después del reset, primer `mark_habit()` hace `streak = 1`
- `pytest -q tests/test_core.py::test_mark_habit_with_gap` pasa
- Caso: last_marked=2 días atrás, mark hoy → streak reinicia

### ☑ T6: core.calculate_streak() + list_habits()
**Dependencia**: T5 (mark completo)  
**RF**: RF-5, RF-7  
**Duración**: ~10 min  
**Hecho cuando**:
- `calculate_streak(habit)` retorna `habit.streak`
- `list_habits(registry)` retorna `[(name, streak, last_marked), ...]`
- `pytest -q tests/test_core.py::test_calculate_streak tests/test_core.py::test_list_habits` pasa

### ☑ T7: core.get_history()
**Dependencia**: T6 (list_habits)  
**RF**: RF-8  
**Duración**: ~10 min  
**Hecho cuando**:
- Retorna lista de `HabitRecord` para un hábito, ordenados cronológicamente
- Si hábito no existe → lista vacía (no error)
- `pytest -q tests/test_core.py::test_get_history` pasa

---

## FASE 3: Persistencia

### ☑ T8: storage.py — load_registry()
**Dependencia**: T1 (models)  
**RF**: RF-10  
**Duración**: ~15 min  
**Hecho cuando**:
- Lee JSON desde ruta, parsea y retorna `Registry`
- Si archivo no existe → retorna `Registry()` vacía (sin error)
- Si JSON inválido → lanza `JSONDecodeError` (no silent fallback)
- `pytest -q tests/test_storage.py::test_load_nonexistent tests/test_storage.py::test_load_corrupted` pasa

### ☑ T9: storage.py — save_registry()
**Dependencia**: T8 (load)  
**RF**: RF-10  
**Duración**: ~15 min  
**Hecho cuando**:
- Serializa `Registry` a JSON con formato legible (indent=2)
- Escribe en ruta con encoding UTF-8
- Si no hay permisos → lanza `PermissionError` (no fallback)
- `pytest -q tests/test_storage.py::test_save_load_roundtrip` pasa

---

## FASE 4: CLI

### ☑ T10: cli.py — comando `register`
**Dependencia**: T7 (core completo) + T9 (storage)  
**RF**: RF-1, RF-2, RF-3, RF-7, RF-9  
**Duración**: ~20 min  
**Hecho cuando**:
- Acepta `python -m habits register <nombre>`
- Llama `core.validate_habit_name()`, si falla → error en español
- Llama `core.register_habit()` → guarda con `storage.save_registry()`
- Imprime con `core.list_habits()` (tabla)
- `pytest -q tests/test_cli.py::test_register_flow` pasa

### ☑ T11: cli.py — comando `mark`
**Dependencia**: T10 (register)  
**RF**: RF-4, RF-6, RF-7  
**Duración**: ~15 min  
**Hecho cuando**:
- Acepta `python -m habits mark <nombre>`
- Llama `core.mark_habit(registry, nombre, date.today())`
- Guarda con `storage.save_registry()`
- Imprime lista actualizada
- Error si hábito no existe (mensaje en español)
- `pytest -q tests/test_cli.py::test_mark_flow` pasa

### ☑ T12: cli.py — comando `list`
**Dependencia**: T11 (mark)  
**RF**: RF-7  
**Duración**: ~10 min  
**Hecho cuando**:
- Acepta `python -m habits list`
- Carga registry, llama `core.list_habits()`
- Imprime tabla: `Hábito | Racha | Último registro`
- Maneja lista vacía sin error
- `pytest -q tests/test_cli.py::test_list_output` pasa

### ☑ T13: cli.py — comando `history`
**Dependencia**: T12 (list)  
**RF**: RF-8  
**Duración**: ~10 min  
**Hecho cuando**:
- Acepta `python -m habits history <nombre>`
- Llama `core.get_history()`, imprime cronológicamente
- Error si hábito no existe (mensaje en español)
- `pytest -q tests/test_cli.py::test_history_output` pasa

---

## FASE 5: Validación y Cobertura

### ☑ T14: test_core.py completo
**Dependencia**: T7 (core completo)  
**RF**: RF-1 a RF-9  
**Duración**: ~25 min  
**Hecho cuando**:
- Todos los test cases de plan.md están en `test_core.py`
- `pytest -q tests/test_core.py -v` pasa 100%
- Cobertura ≥95% para `core.py`
- Incluye: validación, register, mark (sin hueco, con hueco), calculate, list, history

### ☑ T15: test_storage.py completo
**Dependencia**: T9 (storage completo)  
**RF**: RF-10  
**Duración**: ~15 min  
**Hecho cuando**:
- Roundtrip: save → load → idéntico
- Archivo no existe → Registry vacía
- JSON corrupto → excepción (no fallback)
- Missing fields → excepción
- `pytest -q tests/test_storage.py -v` pasa 100%

### ☑ T16: test_cli.py completo
**Dependencia**: T13 (CLI completo)  
**RF**: RF-1 a RF-10  
**Duración**: ~25 min  
**Hecho cuando**:
- Tests para: register, mark, list, history, idempotencia, errores
- Valida output en español
- Valida handling de permisos I/O
- `pytest -q tests/test_cli.py -v` pasa 100%

### ☑ T17: Validación Final
**Dependencia**: T14, T15, T16 (todos los tests)  
**RF**: Todos  
**Duración**: ~10 min  
**Hecho cuando**:
- `pytest -q` pasa sin warnings
- `python -m habits --help` (o similar) funciona
- Zero type hint errors (si usas mypy: `mypy habits/`)
- Constitution.md es respetada: identifiers inglés, UX español, sin deps, type hints
- Spec vs Code son consistentes (case-sensitive, unique names, racha logic, hueco logic)

---

## Resumen de Dependencias

```
T1 (models)
├── T2 (validate)
│   └── T3 (register)
│       └── T4 (mark sin hueco)
│           └── T5 (mark con hueco)
│               ├── T6 (calculate + list)
│               │   └── T7 (history)
│               │       └── T10 (CLI register)
│               │           └── T11 (CLI mark)
│               │               └── T12 (CLI list)
│               │                   └── T13 (CLI history)
│               │                       ├── T14 (test_core)
│               │                       ├── T15 (test_storage)
│               │                       └── T16 (test_cli)
│               │                           └── T17 (validación final)
├── T8 (storage load)
│   └── T9 (storage save)
```

---

## Estimación Total
- **Fase 1**: 15 min
- **Fase 2**: ~95 min (7 tareas)
- **Fase 3**: ~30 min (2 tareas)
- **Fase 4**: ~55 min (4 tareas)
- **Fase 5**: ~75 min (4 tareas)

**Total**: ~270 min (~4.5 horas) — ajustable según expertise.

