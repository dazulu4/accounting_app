#!/bin/bash
# =============================================================================
# Script de Formateo Automático de Código
# =============================================================================
#
# Este script formatea automáticamente el código usando black e isort
# Útil para corregir problemas de formato detectados por quality.sh
#
# Uso:
#   ./scripts/format.sh
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

# --- Lógica Principal ---
main() {
    log_info "🎨 Iniciando formateo automático de código..."
    echo ""

    # Formatear código con Black
    log_info "📝 Formateando código con Black..."
    if poetry run black .; then
        log_success "✅ Black: Código formateado exitosamente"
    else
        log_error "❌ Black: Error al formatear código"
        exit 1
    fi

    # Organizar imports con isort
    log_info "📦 Organizando imports con isort..."
    if poetry run isort .; then
        log_success "✅ isort: Imports organizados exitosamente"
    else
        log_error "❌ isort: Error al organizar imports"
        exit 1
    fi

    echo ""
    log_success "🎉 ¡Formateo completado exitosamente!"
    log_info "💡 Para verificar calidad: ./scripts/quality.sh"
}

# --- Ejecución ---
main 