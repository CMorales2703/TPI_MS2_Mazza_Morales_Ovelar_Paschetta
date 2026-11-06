# Declaración de uso de IA — Cristian Morales

> Antes de entregar: reemplazar **[otra IA]** por el nombre de la herramienta usada para el análisis inicial y confirmar si las decisiones de la preparación fueron del grupo o propias.

## Registro

| Integrante | Herramienta | Para qué la usó | Grado de intervención | Evidencia |
|---|---|---|---|---|
| Cristian Morales | Claude (Anthropic) | **Preparación:** resumen de la consigna, generación del sistema base, configuración del repositorio (README, scripts de arranque, plantilla de PR) y plan de trabajo del equipo | **Alto.** El sistema base y los archivos de configuración fueron generados por la IA. Las decisiones fueron del grupo: elegimos el stack y el dominio, la organización con ramas `main`/`dev`, la protección de ramas y el reparto de tareas | `anexo/ia/cristian_claude_01_preparacion.pdf` |
| Cristian Morales | Claude (Anthropic) | **Diagnóstico:** revisión del análisis inicial, guía para ejecutar los casos y armado de los documentos | **Medio.** La IA revisó el análisis, propuso los casos de prueba y armó los documentos. Yo ejecuté y capturé los casos, evalué cada resultado, redacté el análisis de la ficha (impacto, riesgo, prioridad y principio) y lo corregí a partir de la revisión | `anexo/ia/cristian_claude_02_diagnostico.pdf` |
| Cristian Morales | Claude (Anthropic) | **Pruebas (Fase 2):** guía para aislar la base de datos, revisión de los tests y generación de parte de ellos | **Medio.** Yo escribí el `conftest.py` y los tests de estudiantes (casos 1 a 6, 10, 11 y 12) y los corregí a partir de la revisión de la IA. Decidí el criterio de línea de base. La IA generó los tests de responsables (casos 7, 8a y 8b), aplicó los últimos ajustes del caso 11 y redactó el documento de resultados | `anexo/ia/cristian_claude_03_pruebas.pdf` |
| Cristian Morales | Claude (Anthropic) | **Refactoring (Fase 3):** propuesta de estructura, cambios transversales (conexión, arranque y routers) y refactorings de estudiantes y responsables | **Alto.** La IA propuso la estructura, escribió el código de los refactorings y la documentación de la fase, y verificó que los tests pasaran después de cada commit. Yo elegí aplicar la propuesta, apliqué los cambios en mi repositorio, corregí los problemas que aparecieron al aplicarlos (datos de prueba incompletos, archivos duplicados y formato automático) y verifiqué cada paso con los tests. Los commits llevan a Claude como coautor | `anexo/ia/cristian_claude_04_refactoring.pdf` |

## Detalle

Usé Claude (Anthropic) para preparar el trabajo: resumir la consigna, generar el sistema base y la configuración del repositorio, y armar el plan de trabajo del equipo. Las decisiones de stack, dominio, organización de ramas y reparto de tareas fueron del grupo.

Para el diagnóstico de mi parte (líneas 1–111), lo revisé con Claude, que detectó errores de clasificación y casos que faltaban. Después ejecuté y capturé los 12 casos de prueba, evalué cada resultado según el criterio de códigos HTTP y redacté el análisis de cada hallazgo de la ficha. Las capturas y los documentos fueron organizados con asistencia de la IA.

Verificar el análisis ejecutando el sistema me permitió confirmar un defecto real (error 500 con `email: null`) que el análisis inicial solo había anticipado, y corregir la clasificación de varios smells.

Para las pruebas de mi parte, Claude me guió para aislar la base de datos sin modificar `main.py` y revisó cada test. Escribí el `conftest.py` y los tests de estudiantes, y los corregí a partir de esa revisión. El criterio de línea de base (verificar el comportamiento actual y dejar el esperado en un comentario) lo decidí yo. Los tests de responsables y el documento de resultados los generó la IA a partir del mismo patrón; los revisé y los ejecuté.

En la Fase 3, Claude propuso la estructura del proyecto a partir de las fichas de smells de los cuatro integrantes y escribió los cambios transversales y los refactorings de mi parte, separando los que conservan el comportamiento de los que son corrección de defecto. Apliqué los cambios en mi repositorio paso a paso, verificando con los tests después de cada commit.