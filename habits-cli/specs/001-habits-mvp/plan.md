# Plan: Habits MVP

**Fecha**: 2026-10-02  
**Basado en**: spec.md, constitution.md

---

## Arquitectura Modular

```
habits/
├── __init__.py          # exports públicas
├── __main__.py          # entry point CLI
├── cli.py               # capa CLI (RF-7, RF-8 → UI)
├── core.py              # lógica pura de hábitos y rachas
├── storage.py           # persistencia JSON
└── models.py            # tipos compartidos
```

**Razón**: Constitución #4-6 exige: núcleo puro sin I/O, CLI thin, storage agnóstico. Separación clara de responsabilidades.

---

## Modelo de Datos

### Tipos Python (en `models.py`, type hints obligatorios)

```
Habit:
  - name: str              # alfanuméricos, 1-100 chars, unique, case-sensitive
  - streak: int            # hábitos marcados consecutivos (≥0)
  - last_marked: date      # última marca (para detectar hueco)

HabitRecord:
  - name: str
  - timestamp: datetime    # fecha/hora exacta de cada marca (local, medianoche de PC)

Registry:
  - habits: dict[name → Habit]     # estado actual
  - records: list[HabitRecord]     # histórico completo
```

### Formato JSON (persistido, debe ser versionado)

```json
{
  "version": "1.0",
  "habits": {
    "Ejercicio": {"name": "Ejercicio", "streak": 3, "last_marked": "2026-10-02"},
    "Lectura": {"name": "Lectura", "streak": 0, "last_marked": "2026-09-30"}
  },
  "records": [
    {"name": "Ejercicio", "timestamp": "2026-10-02T08:30:00"},
    {"name": "Lectura", "timestamp": "2026-09-30T20:15:00"}
  ]
}
```

**Decisión**: `last_marked` es `date`, no `datetime` — porque hueco se detecta por **cambio de fecha**, no hora.  
**Alternativa rechazada**: Guardar solo `datetime` sin `date` — requeriría lógica de parsing y comparación más compleja en `core.py`.

---

## Módulos y Responsabilidades

### `models.py`
**Responsabilidad**: Tipos y dataclasses  
**No hacer**: Lógica de negocio, I/O, validación

**Tipos**:
- `Habit` (dataclass)
- `HabitRecord` (dataclass)
- `Registry` (dataclass)

**Cubre**: Base para todos los RF (tipos compartidos)

---

### `core.py` — NÚCLEO PURO (sin I/O)
**Responsabilidad**: Lógica de hábitos y rachas (RF-1, RF-2, RF-3, RF-5, RF-6)  
**Entrada**: `Registry` + comando del usuario  
**Salida**: `Registry` modificado o datos consultados  
**No hacer**: I/O, CLI, persistencia

**Funciones públicas**:

```
def validate_habit_name(name: str) -> bool
  # Retorna True si nombre es válido (alfanuméricos, 1-100)
  # Cubre: RF-9

def register_habit(registry: Registry, name: str) -> Registry
  # Crea nuevo hábito con streak=0
  # Si ya existe, se ignora (idempotencia)
  # Cubre: RF-1, RF-2

def mark_habit(registry: Registry, name: str, today: date) -> Registry
  # Marca hábito como completado hoy
  # Detecta hueco (si last_marked ≠ hoy-1 → reinicia streak a 0)
  # Incrementa streak a streak+1 si no hay hueco
  # Si ya está marcado hoy, se ignora (idempotencia)
  # Cubre: RF-2, RF-4, RF-6

def calculate_streak(habit: Habit) -> int
  # Retorna streak actual (datos ya calculados)
  # Cubre: RF-5

def list_habits(registry: Registry) -> list[dict]
  # Retorna [(name, streak, last_marked), ...]
  # Cubre: RF-7

def get_history(registry: Registry, name: str) -> list[HabitRecord]
  # Retorna histórico de registros para un hábito
  # O lista vacía si no existe
  # Cubre: RF-8
```

**Decisión**: Validación + lógica de racha **en `core.py`**.  
**Alternativa rechazada**: Poner validación en `cli.py` — violaría "núcleo puro" y causaría lógica duplicada.

**Decisión**: `mark_habit` recibe `today: date` como parámetro.  
**Alternativa rechazada**: Que `core.py` llame a `date.today()` — violaría pureza; `core.py` no hace I/O ni syscalls.

---

### `storage.py` — PERSISTENCIA AGNÓSTICA
**Responsabilidad**: Cargar/guardar JSON (RF-10)  
**Entrada**: `Registry` o ruta de archivo  
**Salida**: `Registry` cargada o confirmación de guardado

**Funciones públicas**:

```
def load_registry(path: str = "~/.habits.json") -> Registry
  # Carga JSON, parsea, retorna Registry
  # Si archivo no existe → retorna Registry vacía
  # Si JSON corrupto → lanza excepción (caller decide qué hacer)
  # Cubre: RF-10

def save_registry(registry: Registry, path: str = "~/.habits.json") -> None
  # Serializa Registry a JSON, escribe archivo
  # Si no hay permisos → lanza excepción I/O
  # Cubre: RF-10
```

**Decisión**: Ruta por defecto `~/.habits.json` (agnóstico, es XDG-like).  
**Alternativa rechazada**: `.` (directorio actual) — no portable; `~/` es estándar para CLI.

**Decisión**: JSON corrupto lanza excepción, no fallback silencioso.  
**Alternativa rechazada**: Estado vacío silencioso — data loss silenciosa es peligrosa.

---

### `cli.py` — CAPA THIN
**Responsabilidad**: Parsear args, mapear a `core.py`, formatear salida (RF-7, RF-8, UX español)  
**Entrada**: `sys.argv`  
**Salida**: stdout/stderr

**Comandos**:

```
register <name>
  → core.register_habit() → core.list_habits() → print
  → Cubre: RF-1, RF-2, RF-3, RF-7

mark <name>
  → core.mark_habit() → core.list_habits() → print
  → Cubre: RF-2, RF-4, RF-6, RF-7

list
  → core.list_habits() → print tabla
  → Cubre: RF-7

history <name>
  → core.get_history() → print cronológico
  → Cubre: RF-8
```

**Decisión**: CLI no valida, solo delega a `core.validate_habit_name()`.  
**Alternativa rechazada**: Validación en CLI — duplica lógica.

**Decisión**: Mensajes de error en español, identifiers en inglés.  
**Alternativa rechazada**: Todo en español — code es inglés por convención.

---

## Decisiones Arquitectónicas

| Decisión | Razón | Alternativa rechazada |
|----------|-------|----------------------|
| `core.py` sin I/O, sin syscalls | Constitution #4: núcleo puro | Que `core.py` llame `date.today()` o I/O |
| Validación en `core.py`, no en CLI | DRY; `core` es fuente única | Validar en CLI también |
| `mark_habit(registry, name, today: date)` | `core.py` no puede saber la fecha actual | Que `mark_habit()` llame `date.today()` internamente |
| Hueco = cambio de `date`, no `datetime` | Más simple; una medianoche de PC = nuevo día | Comparar cada hora/minuto |
| JSON corrupto → excepción, no fallback | Data integrity; mejor fallar ruidoso | Silent fallback a Registry vacía |
| Ruta default `~/.habits.json` | Agnóstico, estándar | `./.habits.json` (no portable) |
| Racha mide "hábitos marcados consecutivos" | Intuición: cadena se rompe con un hueco | Racha mide días de calendario |
| Case-sensitive para nombres | Más simple; "Ejercicio" ≠ "ejercicio" | Case-insensitive (más UI-friendly pero más código) |

---

## Estrategia de Tests

### Nivel 1: Unit Tests (`test_core.py`)
**Módulo**: `core.py`  
**Mocks**: `Registry`, `models`; sin I/O

```
test_validate_habit_name
  ✓ "Ejercicio" → True
  ✓ "" → False
  ✓ "Ejercicio 123" → False (espacio)
  ✓ "A"*100 → True
  ✓ "A"*101 → False

test_register_habit
  ✓ Nuevo hábito → streak=0, last_marked=None
  ✓ Registrar 2x → idempotencia (solo 1 en registry)

test_mark_habit (sin hueco)
  ✓ Primer mark hoy → streak=1, last_marked=today
  ✓ Mark 2x hoy → idempotencia (streak=1)
  ✓ Mark ayer, hoy → streak=2
  ✓ Mark ayer, hoy, hoy → streak=2 (idempotencia)

test_mark_habit (con hueco)
  ✓ last_marked=hace 2 días, mark hoy → streak=0→1, hueco detectado
  ✓ last_marked=ayer, skip hoy, mark mañana → hueco → streak reset

test_calculate_streak
  ✓ Retorna valor correcto de Registry

test_list_habits
  ✓ Formato correcto [(name, streak, last_marked), ...]

test_get_history
  ✓ Hábito existe → histórico en orden cronológico
  ✓ Hábito no existe → lista vacía
```

**Cubre**: RF-1, RF-2, RF-3, RF-4, RF-5, RF-6, RF-7, RF-8, RF-9

---

### Nivel 2: Integration Tests (`test_storage.py`)
**Módulo**: `storage.py`  
**Mocks**: File I/O (tempfile)

```
test_save_load_roundtrip
  ✓ Registry → JSON → Registry (idéntico)

test_load_nonexistent_file
  ✓ Retorna Registry vacía

test_load_corrupted_json
  ✓ Lanza JSONDecodeError (no fallback)

test_load_missing_fields
  ✓ Lanza KeyError o ValidationError
```

**Cubre**: RF-10

---

### Nivel 3: E2E Tests (`test_cli.py`)
**Módulo**: `cli.py` + `core.py` + `storage.py`  
**Mocks**: stderr/stdout

```
test_register_flow
  ✓ `register Ejercicio` → mensaje OK → archivo JSON creado

test_mark_flow
  ✓ `mark Ejercicio` → streak=1 → display actualizado

test_list_output
  ✓ `list` → tabla formateada en español

test_history_output
  ✓ `history Ejercicio` → fechas en orden cronológico

test_error_handling
  ✓ Nombre inválido → mensaje de error en español
  ✓ Hábito no existe en `mark` → error claro
  ✓ Permiso denegado al guardar → excepción

test_idempotence
  ✓ 2x `register X` → 1 hábito
  ✓ 2x `mark X` mismo día → streak=1
```

**Cubre**: RF-1 a RF-10

---

## Mapeo RF → Módulo

| RF | Módulo | Función |
|----|--------|---------|
| RF-1: Registrar hábito | `core.py` | `register_habit()` |
| RF-2: Idempotencia | `core.py` | `register_habit()`, `mark_habit()` |
| RF-3: Múltiples por día | `core.py` | `mark_habit()` (soporta dict con keys distintos) |
| RF-4: Marcar cumplido | `cli.py` + `core.py` | comando `mark` → `mark_habit()` |
| RF-5: Calcular racha | `core.py` | `calculate_streak()` |
| RF-6: Reinicio por hueco | `core.py` | `mark_habit()` (detecta fecha) |
| RF-7: Listar + rachas | `cli.py` + `core.py` | `list_habits()` → formato tabla |
| RF-8: Histórico | `cli.py` + `core.py` | `get_history()` → formato cronológico |
| RF-9: Validar nombre | `core.py` | `validate_habit_name()` |
| RF-10: Persistencia JSON | `storage.py` | `load_registry()`, `save_registry()` |

---

## Criterios de Finalización (Verificables)

✅ Estructura de módulos existe (core, cli, storage, models)  
✅ `core.py` tiene 0 imports de I/O (`os`, `sys`, `json`, `pathlib`)  
✅ `pytest -q` pasa 100% (unit + integration + e2e)  
✅ Hueco detectado por `date` change, no por horas  
✅ Validación rechaza nombres con espacios y caracteres especiales  
✅ JSON se carga/guarda sin deps externas (stdlib `json`)  
✅ Type hints en todas las funciones públicas (PEP 484)  
✅ UX en español, code en inglés  
✅ Spec y code son consistentes (valores racha, uniqueness, case-sensitive)  

---

## Notas

- **Racha post-hueco**: Al ejecutar CLI, si `today > last_marked + 1 día`, racha se marca como "roto". Próximo `mark_habit()` inicia nueva cadena con streak=1.
- **Medianoche de PC**: Se usa `date.today()` en `cli.py` para pasar a `core.py`; `core.py` no asume zona horaria.
- **Timestamps**: Se guardan en ISO 8601 local (no UTC) para preservar "cuándo el usuario marcó".
