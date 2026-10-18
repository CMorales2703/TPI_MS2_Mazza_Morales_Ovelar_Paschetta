<#
Uso (Windows):
  .\run.ps1          Prepara el entorno si hace falta y levanta el sistema
  .\run.ps1 test     Prepara el entorno si hace falta y corre los tests
  .\run.ps1 reset    Borra la base y el log para volver a los datos iniciales

Si PowerShell bloquea el script, usar run.bat (hace lo mismo).
#>
param(
    [ValidateSet("run", "test", "reset")]
    [string]$Accion = "run"
)

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$hashFile = Join-Path $PSScriptRoot ".venv\.deps-hash"

function Get-PythonBase {
    foreach ($cmd in @("py", "python")) {
        if (Get-Command $cmd -ErrorAction SilentlyContinue) {
            try {
                & $cmd --version *> $null
                if ($LASTEXITCODE -eq 0) { return $cmd }
            } catch {
                # Acceso directo de la Microsoft Store u otro Python que no responde: probar el siguiente
            }
        }
    }
    throw "No se encontro Python. Instalarlo desde https://www.python.org/downloads/ marcando 'Add Python to PATH'."
}

function Initialize-Entorno {
    if (-not (Test-Path $venvPython)) {
        $py = Get-PythonBase
        Write-Host "Creando entorno virtual..." -ForegroundColor Cyan
        & $py -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw "No se pudo crear el entorno virtual." }
    }

    $hashActual = (Get-FileHash -Path "requirements.txt", "requirements-dev.txt").Hash -join ""
    $hashGuardado = ""
    if (Test-Path $hashFile) { $hashGuardado = ([string](Get-Content $hashFile -Raw)).Trim() }

    if ($hashActual -ne $hashGuardado) {
        Write-Host "Instalando dependencias..." -ForegroundColor Cyan
        & $venvPython -m pip install --quiet --disable-pip-version-check -r requirements-dev.txt
        if ($LASTEXITCODE -ne 0) { throw "Fallo la instalacion de dependencias." }
        Set-Content -Path $hashFile -Value $hashActual
    }
}

switch ($Accion) {
    "reset" {
        Remove-Item -Path "solicitudes.db", "notificaciones.log" -ErrorAction SilentlyContinue
        Write-Host "Listo: el sistema va a arrancar con los datos iniciales." -ForegroundColor Green
    }
    "test" {
        Initialize-Entorno
        & $venvPython -m pytest
        if ($LASTEXITCODE -eq 5) {
            Write-Host "Todavia no hay tests para correr." -ForegroundColor Yellow
            exit 0
        }
        exit $LASTEXITCODE
    }
    "run" {
        Initialize-Entorno
        Write-Host "Sistema en http://127.0.0.1:8000/docs  (Ctrl+C para detener)" -ForegroundColor Green
        & $venvPython -m uvicorn main:app --reload
    }
}
