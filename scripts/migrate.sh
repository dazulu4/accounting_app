#!/bin/bash
# =============================================================================
# Gestión de Migraciones de Base de Datos - Edición Simplificada
# =============================================================================
#
# Este script unificado maneja todo el ciclo de vida de las migraciones de Alembic.
#
# Comandos:
#   new "<mensaje>" : Crea un nuevo archivo de migración.
#   upgrade         : Aplica todas las migraciones pendientes.
#   downgrade       : Revierte la última migración aplicada.
#   current         : Muestra la versión actual de la migración.
#   history         : Muestra el historial de migraciones.
#
# Uso:
#   ./scripts/migrate.sh [comando] [argumentos...]
#
# Ejemplos:
#   ./scripts/migrate.sh new "add_user_email_column"
#   ./scripts/migrate.sh upgrade
#   ./scripts/migrate.sh downgrade
# =============================================================================

set -euo pipefail

# --- Configuración ---
COMMAND="${1:-}"
export APP_ENVIRONMENT="development" # Por defecto para operaciones de migración

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

show_usage() {
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  new \"<mensaje>\" : Crea una nueva migración (ej: 'add_users_table')."
    echo "  upgrade         : Aplica las migraciones pendientes a la base de datos."
    echo "  downgrade       : Revierte la última migración."
    echo "  current         : Muestra la revisión actual."
    echo "  history         : Muestra el historial de revisiones."
    exit 1
}

# --- Validación de Prerrequisitos ---
check_prerequisites() {
    log_info "Verificando que 'alembic' esté disponible..."
    if ! poetry run alembic --version &> /dev/null; then
        log_error "Alembic no está instalado o no se puede ejecutar. Asegúrate de haber ejecutado 'poetry install'."
        exit 1
    fi
    log_success "Alembic está listo."
}

# --- Lógica de Comandos ---
run_new() {
    local message="$1"
    if [ -z "$message" ]; then
        log_error "El comando 'new' requiere un mensaje para la migración."
        echo "Ejemplo: $0 new \"add_user_email_column\""
        exit 1
    fi
    log_info "Generando nuevo archivo de migración: '$message'..."
    if poetry run alembic revision --autogenerate -m "$message"; then
        log_success "Nuevo archivo de migración generado en el directorio 'migration/versions/'."
    else
        log_error "Falló la generación de la migración."
        exit 1
    fi
}

run_upgrade() {
    log_info "Aplicando migraciones a la base de datos (upgrade)..."
    if poetry run alembic upgrade head; then
        log_success "Migraciones aplicadas exitosamente."
    else
        log_error "Falló la aplicación de las migraciones."
        exit 1
    fi
}

run_downgrade() {
    log_info "Revirtiendo la última migración (downgrade)..."
    if poetry run alembic downgrade -1; then
        log_success "Última migración revertida exitosamente."
    else
        log_error "Falló la reversión de la migración."
        exit 1
    fi
}

run_current() {
    log_info "Mostrando la versión actual de la base de datos..."
    poetry run alembic current
}

run_history() {
    log_info "Mostrando el historial de migraciones..."
    poetry run alembic history --verbose
}


# --- Lógica Principal ---
main() {
    if [ -z "$COMMAND" ]; then
        show_usage
    fi

    check_prerequisites

    case "$COMMAND" in
        new)
            run_new "${2:-}"
            ;;
        upgrade)
            run_upgrade
            ;;
        downgrade)
            run_downgrade
            ;;
        current)
            run_current
            ;;
        history)
            run_history
            ;;
        *)
            log_error "Comando desconocido: $COMMAND"
            show_usage
            ;;
    esac
}

# --- Ejecución ---
main "$@" 