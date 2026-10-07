# habits-cli — Guía de Usuario

CLI para registrar hábitos diarios y rastrear rachas consecutivas.

---

## Instalación

```bash
cd habits-cli
pip install -e .
```

O sin instalar, ejecuta directamente con:

```bash
python -m habits <comando>
```

---

## Comandos

### `register <nombre>`
Registra un hábito para hoy. Si ya lo registraste hoy, lo ignora (idempotente).

```bash
python -m habits register Ejercicio
# ✓ 'Ejercicio' registrado. Racha: 1 día(s).

python -m habits register Ejercicio   # segunda vez el mismo día
# 'Ejercicio' ya fue registrado hoy. Racha: 1 día(s).
```

---

### `mark <nombre>`
Igual que `register`. Alias para marcar un hábito como cumplido.

```bash
python -m habits mark Lectura
# ✓ 'Lectura' registrado. Racha: 1 día(s).
```

---

### `list`
Muestra todos los hábitos con su racha actual y último registro.

```bash
python -m habits list
```

```
Hábito                          Racha  Último registro
-------------------------------------------------------
Ejercicio                           5  2026-10-07
Lectura                             2  2026-10-06
Meditacion                          0  nunca
```

---

### `history <nombre>`
Muestra todas las fechas en que fue registrado un hábito, en orden cronológico.

```bash
python -m habits history Ejercicio
```

```
Histórico de 'Ejercicio':
  2026-10-03 00:00:00
  2026-10-04 00:00:00
  2026-10-05 00:00:00
  2026-10-06 00:00:00
  2026-10-07 00:00:00
```

---

## Reglas de nombres

- Solo letras y números (sin espacios ni caracteres especiales)
- Mínimo 1 carácter, máximo 100
- ✅ `Ejercicio`, `Lectura123`, `Yoga`
- ❌ `Ejercicio matutino`, `Hábito`, `Yoga!`

---

## Cómo funciona la racha

- Cada día que registras un hábito, la racha suma 1.
- Si pasas **un día completo sin registrar**, la racha vuelve a 0 al retomar.
- Registrar varias veces el mismo día cuenta como **un solo día**.

```
Día 1: register Ejercicio → Racha: 1
Día 2: register Ejercicio → Racha: 2
Día 3: (no registras)
Día 4: register Ejercicio → Racha: 1  ← reinicio por hueco
```

---

## Persistencia

Los datos se guardan automáticamente en:

```
~/.habits/registry.json
```

No necesitas hacer nada extra; el archivo se crea en el primer uso y persiste entre sesiones.

---

## Flujo típico de uso

```bash
# Mañana: marca tus hábitos del día
python -m habits register Ejercicio
python -m habits register Lectura
python -m habits mark Meditacion

# Ver progreso
python -m habits list

# Revisar historial de un hábito específico
python -m habits history Ejercicio
```
