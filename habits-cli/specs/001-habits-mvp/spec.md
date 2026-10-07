# Spec: Habits MVP

**Fecha**: 2026-10-02  
**Autor**: Judith Paco  
**Estado**: Aprobado

---

## Propósito
Permitir a un usuario registrar hábitos diarios y ver rachas consecutivas de cumplimiento, con persistencia local.

---

## Requerimientos Funcionales (EARS)

### RF-1: Registrar hábito
**Given** un usuario abre el CLI  
**When** ejecuta el comando de registro con nombre válido  
**Then** el hábito se persiste y la racha inicia en 1  
**Why** porque el usuario necesita crear un nuevo hábito para empezar a rastrearlo

### RF-2: Idempotencia de registro
**Given** un hábito ya fue registrado hoy  
**When** el usuario intenta registrar el mismo hábito nuevamente hoy  
**Then** la operación se ignora sin error (no duplica)  
**Why** porque queremos evitar registros múltiples del mismo hábito en un día

### RF-3: Múltiples hábitos por día
**Given** un usuario ha registrado un hábito ya  
**When** registra un hábito *diferente* el mismo día  
**Then** ambos se guardan sin conflicto  
**Why** porque los usuarios necesitan rastrear varios hábitos en paralelo

### RF-4: Seleccionar hábito cumplido
**Given** un usuario quiere marcar un hábito como completado  
**When** ejecuta el comando de selección/cumplimiento para un hábito existente  
**Then** ese hábito se marca registrado hoy (igual que RF-1)  
**Why** porque es una UX alternativa al registro (sintaxis más clara)

### RF-5: Calcular racha consecutiva
**Given** un hábito con registro hoy  
**When** se calcula su racha  
**Then** racha = contador de días consecutivos desde el último registro sin huecos  
**Why** porque la racha es la métrica core de motivación en hábitos

### RF-6: Reinicio de racha por hueco
**Given** un hábito con racha activa  
**When** pasan 24h sin registro (un día completo sin marcar)  
**Then** la racha se reinicia a 0 al siguiente registro  
**Why** porque la racha mide *consecutividad* — un hueco rompe la cadena

### RF-7: Listar hábitos + rachas
**Given** un usuario quiere ver su progreso  
**When** ejecuta comando de listado  
**Then** muestra todos los hábitos con su racha actual y último registro (fecha/hora)  
**Why** porque necesita una vista consolidada de su estado

### RF-8: Ver histórico de hábito
**Given** un usuario quiere investigar el historial de un hábito  
**When** ejecuta comando de histórico con nombre de hábito  
**Then** muestra todas las fechas/horas en que fue registrado, en orden cronológico  
**Why** porque necesita auditar y entender patrones de cumplimiento

### RF-9: Validar nombre de hábito
**Given** un usuario intenta registrar un hábito  
**When** el nombre está vacío, contiene caracteres especiales, o excede 100 caracteres  
**Then** se rechaza con mensaje de error claro  
**Why** porque nombres inválidos causan corrupción de datos y UX pobre

### RF-10: Persistencia JSON
**Given** hábitos registrados en sesión  
**When** el usuario cierra el CLI  
**Then** todos los datos se guardan en JSON local y se cargan en siguiente sesión  
**Why** porque sin persistencia, el histórico de rachas se pierde entre ejecuciones

---

## Fuera de Alcance

- ❌ Multi-usuario o autenticación
- ❌ Editar/renombrar/borrar hábitos
- ❌ Estadísticas avanzadas (max racha, % cumplimiento anual)
- ❌ Sincronización en cloud
- ❌ UI gráfica (solo CLI)
- ❌ Recordatorios/notificaciones
- ❌ Import/export de datos
- ❌ Reset de racha manual

---

## Criterios de Finalización

✅ `pytest -q` pasa 100% (todos los RF con cobertura)  
✅ CLI acepta comandos: `register`, `mark`, `list`, `history`  
✅ JSON persiste y carga correctamente en siguiente sesión  
✅ Validación rechaza nombres inválidos  
✅ Racha reinicia correctamente después de un hueco  
✅ Idempotencia: registrar 2x hoy = 1 registro  
✅ Histórico muestra orden cronológico exacto (fecha/hora)  
✅ AGENTS.md y constitution.md son respetados (sin deps externas, type hints, UX español)

---

## Notas
- Timestamp se registra en UTC o local según decisión de implementación (será spec de `storage.py`)
- "Hueco" = 24h sin registro; se valida al comparar fecha de hoy vs última fecha guardada
