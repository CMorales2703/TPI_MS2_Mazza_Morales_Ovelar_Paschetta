## Tipo de cambio
- [ ] `refactor` — mejora interna sin cambiar el comportamiento externo
- [ ] `test` — casos de prueba
- [ ] `docs` — documentación, README o evidencias
- [ ] `chore` — configuración del repo o herramientas
- [ ] `fix` — corrección de un comportamiento incorrecto

**Etapa del TPI:**
<!-- diagnóstico / pruebas / refactoring / code review / documentación -->

## Qué cambia
<!-- Resumen breve de lo que hace este PR -->

## Por qué
<!-- Solo para refactors: completar con la tabla de deuda técnica -->
- **Smell que resuelve:** <!-- ID o nombre en la tabla de smells -->
- **Técnica de refactoring:** <!-- Extract Method, Move Method, Introduce Parameter Object, etc. -->
- **Principio SOLID / Clean Code:** <!-- SRP, OCP, DIP, nombres, manejo de errores, etc. -->

## Antes / después
<!-- Fragmento de código o captura del antes y del después -->

## Verificación
- [ ] Corrí **toda** la suite de tests y está en verde
- [ ] El comportamiento externo no cambió (o el cambio está justificado arriba)
- [ ] Probé manualmente los endpoints afectados desde `/docs`

**Evidencia:** <!-- captura o salida de pytest -->

## Checklist del autor
- [ ] Un commit por cambio lógico, con mensaje claro
- [ ] Mi rama está actualizada con `main`
- [ ] No hay cambios de formato ajenos al PR (reformateo automático, espacios, finales de línea)
- [ ] Solo toqué archivos relacionados con este cambio

## Uso de IA
- [ ] No usé IA en este PR
- [ ] Usé IA: <!-- herramienta, para qué y dónde quedó guardada la evidencia -->
