#!/bin/bash
# =============================================================================
# Ejecución de Pruebas - Edición Simplificada
# =============================================================================
#
# Este script simplificado maneja la ejecución de las pruebas del proyecto.
#
# Comandos:
#   unit        : Ejecuta solo las pruebas unitarias (rápidas).
#   all         : Ejecuta todas las pruebas (por defecto).
#
# Opciones:
#   --coverage  : Muestra un reporte de cobertura de pruebas en la terminal.
#
# Uso:
#   ./scripts/test.sh [comando] [--coverage]
#
# Ejemplos:
#   ./scripts/test.sh
#   ./scripts/test.sh unit --coverage
# =============================================================================

set -euo pipefail

# --- Configuración ---
TEST_TYPE="${1:-all}"
COVERAGE_ENABLED=false
if [[ "${2:-}" == "--coverage" ]]; then
    COVERAGE_ENABLED=true
fi

# Colores para la salida
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}
log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}
log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# --- Lógica Principal ---
main() {
    log_info "🚀 Iniciando la ejecución de pruebas..."
    log_info "Tipo de pruebas: $TEST_TYPE"

    # Construir el comando base de pytest
    PYTEST_CMD="poetry run pytest"

    # Añadir el marcador del tipo de prueba si no es 'all'
    if [ "$TEST_TYPE" != "all" ]; then
        PYTEST_CMD="$PYTEST_CMD -m $TEST_TYPE"
    fi

    # Añadir flags de cobertura si está habilitado
    if [ "$COVERAGE_ENABLED" = true ]; then
        log_info "Análisis de cobertura HABILITADO."
        PYTEST_CMD="$PYTEST_CMD --cov"
    fi
    
    # Ejecutar el comando
    log_info "Ejecutando: $PYTEST_CMD"
    echo "" # Línea en blanco para separar la salida

    if eval "$PYTEST_CMD"; then
        log_success "🎉 ¡Todas las pruebas pasaron exitosamente!"
    else
        log_error "Algunas pruebas fallaron."
        exit 1
    fi
}

# --- Ejecución ---
main 