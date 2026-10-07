# Constitución — habits-cli

## Stack & Dependencias
1. **Python 3.12+** con type hints obligatorios en APIs públicas
2. **Solo stdlib** (pytest exclusivamente para tests)
3. **Persistencia JSON local** — sin bases de datos

## Arquitectura
4. **Núcleo puro** (`habits/core.py`) sin I/O; lógica de rachas ahí
5. **CLI thin** (`habits/cli.py`) — mapeo de args → core
6. **Storage agnóstico** (`habits/storage.py`) — intercambiable sin tocar core

## Calidad & Tests
7. **pytest -q pasa siempre** — gate obligatorio antes de merge
8. **Identifiers en inglés, UX en español** — no mezclar
9. **Spec es fuente de verdad** — no cambies JSON ni core sin spec primero

## Límites
10. **Cero breaking changes sin versionado** en formato JSON
11. **Dependencias nuevas = rechazadas** — incluso si simplificarían código
