# Checklist de code review

**Coordinación:** Isaias Javier Ovelar
**Alcance:** todos los pull requests a `dev` y a `main` del trabajo. Cada PR necesita al menos una aprobación de otro integrante (`main` y `dev` están protegidas) y se integra con merge commit, para conservar cada commit como evidencia.

## Criterios y aceptación

| # | Criterio | Se acepta cuando | Cómo se verifica |
|---|---|---|---|
| 1 | La suite pasa | `pytest` en verde sobre la rama combinada con `dev` | `.\run.bat test` después de traer `dev` |
| 2 | Refactoring seguro | Ningún assert de la línea de base (`etapa-tests`) fue modificado. Si una respuesta cambia, no es refactoring: va en un commit `fix:` aparte | `git diff etapa-tests -- tests` sin líneas `assert` borradas |
| 3 | Un cambio por commit | Cada refactoring en su propio commit, con prefijo (`refactor:`, `test:`, `docs:`, `fix:`) y un mensaje que dice qué y por qué | Historial del PR |
| 4 | Trazabilidad | El commit o el documento cita el hallazgo de la ficha que resuelve y el principio que aplica | `docs/refactoring/<nombre>_refactoring.md` |
| 5 | Alcance | Solo toca la parte del autor o un módulo común acordado; sin cambios de formato ajenos al objetivo | Archivos del PR |
| 6 | Nombres y estructura | Nombres expresivos; funciones con una sola responsabilidad; sin código muerto ni comentado | Lectura del diff |
| 7 | Sin duplicación nueva | Reutiliza lo que ya existe en `app/dominio.py`, `app/validaciones.py` o `app/db.py` | Lectura del diff |
| 8 | Documentación | Antes y después en `docs/refactoring/`; evidencia de la corrida en `docs/evidencias/` | Archivos del PR |
| 9 | Uso de IA declarado | Fila en `docs/uso-ia/<nombre>.md` con herramienta, finalidad y grado, y evidencia en `anexo/ia/` | Archivos del PR |
| 10 | Repositorio limpio | Sin `__pycache__`, bases de datos, archivos duplicados ni nombres con `(1)` | `git status` y archivos del PR |

## Aplicación sobre los PRs de la etapa de refactoring

✓ = cumple · ✗ = no cumple (con la acción tomada) · — = no aplica

| PR | Autor | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | Resultado |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| #13 transversales | Cristian | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | — | ✓ | ✓ | ✓ | Aprobado con observación |
| #17 consultas | Bruno | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | Aprobado; la declaración de IA de la fase se completó en #21 |
| #18 estudiantes y responsables | Cristian | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Aprobado |
| #19 solicitudes | Gaston | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Aprobado |
| #22 estados | Javier | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Aprobado |

## Observaciones y correcciones

| PR | Observación | Criterio | Feedback | Corrección |
|---|---|---|---|---|
| #4 y #9 (tests) | Dos `conftest.py` con diseños distintos: base nueva por test y base compartida con borrado manual | 1, 7 | Con la base compartida, lo que crea un test lo ve el siguiente, y los 500 quedaban ocultos para toda la suite | Un solo `conftest.py` con base por test y un `client_sin_excepciones` solo para los tests que esperan 500 |
| #4 (tests de Cristian) | Los docstrings citaban el número de caso como número de hallazgo | 4 | La relación test → caso → hallazgo tiene que coincidir con la ficha | Corregido antes del merge |
| #7 (diagnóstico de Javier) | Evaluaciones inconsistentes en los casos 10, 12c y 19 | 4 | El caso 10 figura como correcto pero se usa como evidencia de un defecto | Registrado para unificar el criterio en el informe |
| #10 (diagnóstico de Gaston) | La fila del diagnóstico en `docs/uso-ia/gaston.md` no tiene la columna de evidencia | 9 | La tabla se rompe en GitHub y la declaración queda sin evidencia | Pendiente del autor |
| #13 (transversales) | El commit 1 incluye el formato automático del editor sobre todo `main.py` | 5 | El diff muestra más líneas cambiadas que las movidas | Aclarado en la descripción del PR; los commits siguientes, sin formato automático |
| #13 (transversales) | Antes del push faltaba `app/__init__.py` y había routers guardados como `nombre (1).py` | 10 | Python no reconoce los módulos con `(1)` | Corregido antes del push |
| #15 (README) | El README decía que los tags de etapa iban en `dev`, pero el grupo los pone en `main` | 8 | La documentación tiene que reflejar lo que se hace | Corregido |
| #8 / #21 (Bruno) | La declaración de IA del diagnóstico citaba un PDF que no estaba en el repositorio | 9 | Toda evidencia citada tiene que existir | Reemplazado por `anexo/ia/bruno_registro_ia.md` (#21) |
| #19 y #22 | Revisados contra `dev`: sin conflictos, suite en verde, ningún assert modificado | 1, 2 | — | Aprobados |
