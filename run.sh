#!/usr/bin/env bash
# Uso (Linux / macOS):
#   ./run.sh          Prepara el entorno si hace falta y levanta el sistema
#   ./run.sh test     Prepara el entorno si hace falta y corre los tests
#   ./run.sh reset    Borra la base y el log para volver a los datos iniciales
set -euo pipefail
cd "$(dirname "$0")"

ACCION="${1:-run}"
VENV_PY=".venv/bin/python"
HASH_FILE=".venv/.deps-hash"

preparar_entorno() {
  if [ ! -x "$VENV_PY" ]; then
    command -v python3 >/dev/null || { echo "No se encontro python3."; exit 1; }
    echo "Creando entorno virtual..."
    python3 -m venv .venv
  fi

  if command -v sha256sum >/dev/null; then HASH="sha256sum"; else HASH="shasum -a 256"; fi
  actual=$(cat requirements.txt requirements-dev.txt | $HASH | cut -d' ' -f1)
  guardado=$(cat "$HASH_FILE" 2>/dev/null || true)

  if [ "$actual" != "$guardado" ]; then
    echo "Instalando dependencias..."
    "$VENV_PY" -m pip install --quiet --disable-pip-version-check -r requirements-dev.txt
    echo "$actual" > "$HASH_FILE"
  fi
}

case "$ACCION" in
  run)
    preparar_entorno
    echo "Sistema en http://127.0.0.1:8000/docs  (Ctrl+C para detener)"
    exec "$VENV_PY" -m uvicorn main:app --reload
    ;;
  test)
    preparar_entorno
    set +e
    "$VENV_PY" -m pytest
    codigo=$?
    if [ "$codigo" -eq 5 ]; then
      echo "Todavia no hay tests para correr."
      exit 0
    fi
    exit "$codigo"
    ;;
  reset)
    rm -f solicitudes.db notificaciones.log
    echo "Listo: el sistema va a arrancar con los datos iniciales."
    ;;
  *)
    echo "Uso: ./run.sh [run|test|reset]"
    exit 1
    ;;
esac
