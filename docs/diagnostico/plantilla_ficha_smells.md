# Plantilla — Ficha de deuda técnica y code smells

Cada integrante copia esta plantilla como `docs/diagnostico/<nombre>_ficha_smells.md` y la completa sobre su parte del código. Las fichas se unifican después en [`tabla_deuda_tecnica.md`](tabla_deuda_tecnica.md).

Ejemplo completo: [`cristian_ficha_smells.md`](cristian_ficha_smells.md).

## Reglas para completarla

- **Líneas:** siempre las del tag `estado-inicial`, aunque `main.py` ya haya cambiado en `dev`.
- **Cantidad:** al menos 3 hallazgos por integrante.
- **Campos obligatorios:** los 6 de la consigna (nombre, evidencia, ubicación, impacto, riesgo de mantenimiento y prioridad con justificación), más el principio que viola y el refactoring propuesto. Un hallazgo con un campo vacío no entra en la tabla grupal.
- **Nombre:** usar el nombre del catálogo de smells en inglés (Long Method, Duplicated Code, Long Parameter List, etc.). Si es un problema de diseño sin nombre de catálogo, aclararlo debajo del resumen.
- **Evidencia:** un fragmento corto del código, copiado tal cual, entre comillas invertidas.
- **Casos:** los números de caso de `<nombre>_resultados_fase1.md` que muestran el problema desde afuera. Si no hay ninguno, poner `—`.
- **Prioridad:** usar el criterio común de abajo y justificarla en una frase.
- **Refactoring propuesto:** la técnica que lo resolvería (Extract Method, Introduce Parameter Object, Move Method, Replace Conditional with Polymorphism, etc.) o `mejora futura` si no se va a resolver en este trabajo.
- **Transversal:** marcar `Sí` si el problema aparece en la parte de otro integrante o si resolverlo cambia código de otro. Esos hallazgos se resuelven primero, en la Fase 3.

## Criterio común de prioridad

| Prioridad | Cuándo corresponde |
|---|---|
| Alta | Hay un defecto comprobado en las pruebas de la Fase 1, o el problema impide escribir tests confiables |
| Media | Dificulta el mantenimiento o el cambio, pero no se comprobó una falla |
| Baja | Afecta principalmente la legibilidad |

---

# Fase 1 — Ficha de deuda técnica y code smells

**Integrante:** <Nombre y apellido>
**Alcance:** líneas <desde>–<hasta> de `main.py` (tag `estado-inicial`): <funciones>
**Endpoints:** <método y ruta de cada endpoint>
**Evidencia de calidad externa:** [`<nombre>_resultados_fase1.md`](<nombre>_resultados_fase1.md) (los números de caso remiten a esa tabla)
**Uso de IA:** [`docs/uso-ia/<nombre>.md`](../uso-ia/<nombre>.md)

## Resumen

| # | Smell / hallazgo | Ubicación | Casos | Prioridad | Transversal | Refactoring propuesto |
|---|---|---|---|---|---|---|
| 1 | | Líneas | | | | |
| 2 | | Líneas | | | | |
| 3 | | Líneas | | | | |

## Criterio de priorización

| Prioridad | Hallazgos | Por qué |
|---|---|---|
| Alta | | |
| Media | | |
| Baja | | |

**Orden de resolución propuesto:** <qué conviene resolver primero y por qué>

---

## Detalle

### 1. <Nombre del smell>
- **Ubicación:** <función>, líneas <desde>–<hasta>
- **Evidencia:** `<fragmento de código>`
- **Casos:** <números de caso o —>
- **Impacto:** <qué se complica hoy al leer, probar o cambiar este código>
- **Riesgo de mantenimiento:** <qué puede salir mal en un cambio futuro>
- **Prioridad:** <alta / media / baja>, porque <justificación según el criterio común>
- **Principio:** <principio SOLID o práctica de Clean Code que viola>
- **Transversal:** <Sí / No; si es Sí, con qué parte se cruza>
- **Refactoring propuesto:** <técnica, o mejora futura>

### 2. <Nombre del smell>
- **Ubicación:**
- **Evidencia:**
- **Casos:**
- **Impacto:**
- **Riesgo de mantenimiento:**
- **Prioridad:**
- **Principio:**
- **Transversal:**
- **Refactoring propuesto:**

### 3. <Nombre del smell>
- **Ubicación:**
- **Evidencia:**
- **Casos:**
- **Impacto:**
- **Riesgo de mantenimiento:**
- **Prioridad:**
- **Principio:**
- **Transversal:**
- **Refactoring propuesto:**

---

## Para la puesta en común del grupo

- **Hallazgos transversales:** <números y con qué parte se cruzan>
- **Coordinación con otros integrantes:** <hallazgos que tocan código de otro>
- **Propuestas para la tabla grupal:** <smells que afectan a todo `main.py`>
