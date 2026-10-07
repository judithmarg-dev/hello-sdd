# AGENTS.md — habits-cli

## Proyecto
CLI en Python para registrar habitos de estudio y calcular rachas de dias consecutivas. Nucleo puro (`habits/core.py`) + capa CLI (`habits/cli.py`).
Persistencia en JSON local (`habits/storage.py`).

## Comandos
- Ejecutar: `python -m habits <comando>`
- Tests: `pytest -q`

## Estilo y convenciones
- Python 3.12+, type hints en todas las funciones publicas.
- Solo biblioteca estandar (pytest unicamente para tests)
- Identificadores en ingles, mensahes de usuario en spanish.

## Reglas
- Lee `docs/constitution.md` y la spec activa en `specs/` antes de tocar código.
- No agregues dependencias ni cambies el formato del JSON sin actualizar antes la spec.
- No modifiques archivos dentro de `specs/` salvo peticion explicita.

## Al terminar cualquier tarea
- Ejecuta `pytest -q` y confirma en tu respuesta que todo pasa.