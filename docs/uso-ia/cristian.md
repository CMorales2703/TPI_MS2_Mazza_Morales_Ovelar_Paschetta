# Declaración de uso de IA — Cristian Morales

> Antes de entregar: reemplazar **[otra IA]** por el nombre de la herramienta usada para el análisis inicial y confirmar si las decisiones de la preparación fueron del grupo o propias.

## Registro

| Integrante | Herramienta | Para qué la usó | Grado de intervención | Evidencia |
|---|---|---|---|---|
| Cristian Morales | Claude (Anthropic) | **Preparación:** resumen de la consigna, generación del sistema base, configuración del repositorio (README, scripts de arranque, plantilla de PR) y plan de trabajo del equipo | **Alto.** El sistema base y los archivos de configuración fueron generados por la IA. Las decisiones fueron del grupo: elegimos el stack y el dominio, la organización con ramas `main`/`dev`, la protección de ramas y el reparto de tareas | `anexo/ia/cristian_claude_01_preparacion.pdf` |
| Cristian Morales | Claude (Anthropic) | **Diagnóstico:** revisión del análisis inicial, guía para ejecutar los casos y armado de los documentos | **Medio.** La IA revisó el análisis, propuso los casos de prueba y armó los documentos. Yo ejecuté y capturé los casos, evalué cada resultado, redacté el análisis de la ficha (impacto, riesgo, prioridad y principio) y lo corregí a partir de la revisión | `anexo/ia/cristian_claude_02_diagnostico.pdf` |

## Detalle

Usé Claude (Anthropic) para preparar el trabajo: resumir la consigna, generar el sistema base y la configuración del repositorio, y armar el plan de trabajo del equipo. Las decisiones de stack, dominio, organización de ramas y reparto de tareas fueron del grupo.

Para el diagnóstico de mi parte (líneas 1–111), lo revisé con Claude, que detectó errores de clasificación y casos que faltaban. Después ejecuté y capturé los 12 casos de prueba, evalué cada resultado según el criterio de códigos HTTP y redacté el análisis de cada hallazgo de la ficha. Las capturas y los documentos fueron organizados con asistencia de la IA.

Verificar el análisis ejecutando el sistema me permitió confirmar un defecto real (error 500 con `email: null`) que el análisis inicial solo había anticipado, y corregir la clasificación de varios smells.
