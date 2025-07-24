#!/bin/bash
# =============================================================================
# Script de Calidad de Código - Versión Consolidada
# =============================================================================
#
# Este script ejecuta todas las herramientas de calidad de código en orden:
# 1. Black: Formateo automático de código
# 2. isort: Organización de imports
# 3. autoflake: Limpieza de imports no utilizados
# 4. mypy: Verificación de tipos
# 5. flake8: Linter final
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
    echo -e "${GREEN}[SUCCESS]${NC} ✅ $1"
}
log_error() {
    echo -e "${RED}[ERROR]${NC} ❌ $1"
}
log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} ⚠️  $1"
}

# Función para contar problemas
count_issues() {
    local output="$1"
    local count=$(echo "$output" | grep -c "error:" || echo "0")
    echo $count
}

# --- Funciones de Calidad ---

run_black() {
    log_info "🎨 Formateando código con Black..."
    if poetry run black . --quiet; then
        log_success "Black: Código formateado exitosamente"
    else
        log_error "Black: Error al formatear código"
        return 1
    fi
}

run_isort() {
    log_info "📦 Organizando imports con isort..."
    if poetry run isort . --quiet; then
        log_success "isort: Imports organizados exitosamente"
    else
        log_error "isort: Error al organizar imports"
        return 1
    fi
}

run_autoflake() {
    log_info "🧹 Limpiando imports no utilizados con autoflake..."
    
    # Verificar si autoflake está instalado
    if ! poetry run autoflake --version >/dev/null 2>&1; then
        log_warning "autoflake no está instalado. Instalando..."
        poetry add --group dev autoflake --quiet
    fi
    
    # Contar imports no utilizados antes
    before_count=$(poetry run flake8 . --count --select=F401 2>/dev/null | wc -l || echo "0")
    
    # Ejecutar autoflake para eliminar imports no utilizados
    if poetry run autoflake --in-place --remove-all-unused-imports --recursive . --quiet; then
        # Contar imports no utilizados después
        after_count=$(poetry run flake8 . --count --select=F401 2>/dev/null | wc -l || echo "0")
        reduction=$((before_count - after_count))
        
        if [ "$reduction" -gt 0 ]; then
            log_success "autoflake: Eliminados $reduction imports no utilizados"
        else
            log_success "autoflake: No se encontraron imports no utilizados"
        fi
    else
        log_warning "autoflake: No se pudieron eliminar imports no utilizados"
    fi
}

run_mypy() {
    log_info "🔍 Verificando tipos con mypy..."
    mypy_output=$(poetry run mypy . --no-error-summary 2>&1 || true)
    mypy_errors=$(count_issues "$mypy_output")
    
    if [ "$mypy_errors" -eq 0 ]; then
        log_success "mypy: Sin problemas de tipos detectados"
    else
        log_warning "mypy: $mypy_errors problemas de tipos detectados"
        echo "$mypy_output" | head -10
        if [ "$mypy_errors" -gt 10 ]; then
            echo "... y $((mypy_errors - 10)) problemas más"
        fi
    fi
}

run_flake8() {
    log_info "🔎 Ejecutando linter flake8..."
    flake8_output=$(poetry run flake8 . 2>&1 || true)
    flake8_errors=$(echo "$flake8_output" | wc -l)
    
    if [ "$flake8_errors" -eq 0 ]; then
        log_success "flake8: Sin problemas de estilo detectados"
    else
        log_warning "flake8: $flake8_errors problemas de estilo detectados"
        echo "$flake8_output" | head -10
        if [ "$flake8_errors" -gt 10 ]; then
            echo "... y $((flake8_errors - 10)) problemas más"
        fi
    fi
}

# --- Lógica Principal ---
main() {
    log_info "🚀 Iniciando proceso completo de calidad de código..."
    echo ""

    local exit_code=0

    # Paso 1: Formateo automático con Black
    run_black || exit_code=1
    
    # Paso 2: Organización de imports con isort
    run_isort || exit_code=1
    
    # Paso 3: Limpieza de imports no utilizados
    run_autoflake
    
    # Paso 4: Verificación de tipos
    run_mypy
    
    # Paso 5: Linter final
    run_flake8

    # --- Resumen Final ---
    echo ""
    echo "============================================================================="
    echo "📊 RESUMEN DE CALIDAD DE CÓDIGO"
    echo "============================================================================="
    
    # Contar archivos Python
    python_files=$(find . -name "*.py" -not -path "./.venv/*" -not -path "./.git/*" | wc -l)
    echo "📁 Archivos Python analizados: $python_files"
    
    # Obtener estadísticas finales
    mypy_output=$(poetry run mypy . --no-error-summary 2>&1 || true)
    mypy_errors=$(count_issues "$mypy_output")
    
    flake8_output=$(poetry run flake8 . 2>&1 || true)
    flake8_errors=$(echo "$flake8_output" | wc -l)
    
    echo "🔍 Problemas detectados:"
    echo "   • mypy: $mypy_errors errores de tipos"
    echo "   • flake8: $flake8_errors problemas de estilo"
    
    # Calcular score de calidad
    total_issues=$((mypy_errors + flake8_errors))
    if [ "$total_issues" -eq 0 ]; then
        quality_status="EXCELENTE"
    elif [ "$total_issues" -lt 50 ]; then
        quality_status="BUENA"
    elif [ "$total_issues" -lt 100 ]; then
        quality_status="MEJORABLE"
    else
        quality_status="REQUIERE ATENCIÓN"
    fi
    
    echo "📈 Calidad general: $quality_status"
    echo ""
    
    if [ $exit_code -eq 0 ]; then
        log_success "🎉 ¡Proceso de calidad completado exitosamente!"
        log_info "💡 Para ejecutar pruebas unitarias: ./scripts/test.sh"
    else
        log_warning "⚠️  Algunos pasos del proceso de calidad fallaron."
        log_info "💡 Revisa los warnings y corrige los problemas críticos."
    fi
}

# --- Ejecución ---
main 