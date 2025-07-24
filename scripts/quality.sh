#!/bin/bash
# =============================================================================
# Script de Calidad de Código - Sin Pruebas Unitarias
# =============================================================================
#
# Este script ejecuta todas las herramientas de calidad de código
# excepto las pruebas unitarias (que ya tienes en test.sh)
#
# Herramientas incluidas:
# - black: Formateador de código
# - isort: Organizador de imports
# - mypy: Verificador de tipos
# - flake8: Linter adicional
#
# Uso:
#   ./scripts/quality.sh
# =============================================================================

set -euo pipefail

# Colores para la salida
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
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
log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# --- Funciones de Calidad ---
run_black() {
    log_info "🎨 Formateando código con Black..."
    if poetry run black . --check; then
        log_success "✅ Black: Código correctamente formateado"
    else
        log_warning "⚠️  Black: Código necesita formateo"
        log_info "💡 Ejecuta: poetry run black ."
        return 1
    fi
}

run_isort() {
    log_info "📦 Organizando imports con isort..."
    if poetry run isort . --check-only; then
        log_success "✅ isort: Imports correctamente organizados"
    else
        log_warning "⚠️  isort: Imports necesitan organización"
        log_info "💡 Ejecuta: poetry run isort ."
        return 1
    fi
}

run_mypy() {
    log_info "🔍 Verificando tipos con mypy..."
    if poetry run mypy .; then
        log_success "✅ mypy: Verificación de tipos exitosa"
    else
        log_warning "⚠️  mypy: Problemas de tipos detectados"
        return 1
    fi
}

run_flake8() {
    log_info "🔎 Ejecutando linter flake8..."
    if poetry run flake8 .; then
        log_success "✅ flake8: Sin problemas de estilo detectados"
    else
        log_warning "⚠️  flake8: Problemas de estilo detectados"
        return 1
    fi
}

# --- Lógica Principal ---
main() {
    log_info "🚀 Iniciando verificación de calidad de código..."
    echo ""

    local exit_code=0

    # Ejecutar herramientas de calidad
    run_black || exit_code=1
    run_isort || exit_code=1
    run_mypy || exit_code=1
    run_flake8 || exit_code=1

    echo ""
    if [ $exit_code -eq 0 ]; then
        log_success "🎉 ¡Todas las verificaciones de calidad pasaron!"
        log_info "💡 Para ejecutar pruebas unitarias: ./scripts/test.sh"
    else
        log_error "❌ Algunas verificaciones de calidad fallaron."
        log_info "💡 Revisa los warnings y corrige los problemas."
        exit 1
    fi
}

# --- Ejecución ---
main 