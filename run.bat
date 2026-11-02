@echo off
rem Atajo para Windows: ejecuta run.ps1 sin depender de la politica de scripts.
rem Uso: run.bat  |  run.bat test  |  run.bat reset  (o doble clic para levantar el sistema)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1" %*
if errorlevel 1 pause
