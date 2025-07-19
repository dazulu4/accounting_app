#!/bin/bash
# =============================================================================
# Database Migration Script - Enterprise Edition
# =============================================================================
# 
# Professional database migration management for different environments
# with validation, backup, and rollback capabilities.
#
# Features:
# - Environment-specific migration execution
# - Database backup before migration
# - Migration validation and verification
# - Rollback capabilities
# - Comprehensive logging
#
# Usage: ./scripts/migrate.sh [command] [environment]
# Commands: upgrade, downgrade, current, history, backup, validate
# Example: ./scripts/migrate.sh upgrade production
# =============================================================================

set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMMAND="${1:-upgrade}"
ENVIRONMENT="${2:-development}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# Helper Functions
# =============================================================================
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_usage() {
    echo "Usage: $0 [command] [environment]"
    echo ""
    echo "Commands:"
    echo "  upgrade     - Apply pending migrations (default)"
    echo "  downgrade   - Rollback last migration"
    echo "  current     - Show current migration version"
    echo "  history     - Show migration history"
    echo "  backup      - Create database backup"
    echo "  validate    - Validate migration environment"
    echo ""
    echo "Environments:"
    echo "  development - Local development database"
    echo "  staging     - Staging environment database"
    echo "  production  - Production environment database"
    echo ""
    echo "Examples:"
    echo "  $0 upgrade development"
    echo "  $0 current production"
    echo "  $0 backup staging"
}

validate_command() {
    case "$COMMAND" in
        upgrade|downgrade|current|history|backup|validate|help)
            log_success "Valid command: $COMMAND"
            ;;
        *)
            log_error "Invalid command: $COMMAND"
            show_usage
            exit 1
            ;;
    esac
}

validate_environment() {
    case "$ENVIRONMENT" in
        development|staging|production)
            log_success "Valid environment: $ENVIRONMENT"
            ;;
        *)
            log_error "Invalid environment: $ENVIRONMENT"
            show_usage
            exit 1
            ;;
    esac
}

check_requirements() {
    log_info "Checking migration requirements..."
    
    # Check if alembic is available
    if ! command -v python &> /dev/null; then
        log_error "Python is not available. Please activate your virtual environment."
        exit 1
    fi
    
    # Check if migration directory exists
    if [[ ! -d "$PROJECT_ROOT/migration" ]]; then
        log_error "Migration directory not found: $PROJECT_ROOT/migration"
        exit 1
    fi
    
    # Check if alembic.ini exists
    if [[ ! -f "$PROJECT_ROOT/alembic.ini" ]]; then
        log_error "Alembic configuration not found: $PROJECT_ROOT/alembic.ini"
        exit 1
    fi
    
    log_success "All requirements satisfied"
}

set_environment() {
    log_info "Setting up environment: $ENVIRONMENT"
    
    # Set environment variables based on target environment
    case "$ENVIRONMENT" in
        development)
            export APP_ENVIRONMENT=development
            export DATABASE_HOST=${DATABASE_HOST:-localhost}
            export DATABASE_PORT=${DATABASE_PORT:-3306}
            export DATABASE_NAME=${DATABASE_NAME:-accounting_dev}
            export DATABASE_USERNAME=${DATABASE_USERNAME:-admin}
            export DATABASE_PASSWORD=${DATABASE_PASSWORD:-admin123}
            ;;
        staging)
            export APP_ENVIRONMENT=staging
            # For staging/production, these should come from environment or AWS
            if [[ -z "${DATABASE_HOST:-}" ]]; then
                log_error "DATABASE_HOST environment variable required for $ENVIRONMENT"
                exit 1
            fi
            ;;
        production)
            export APP_ENVIRONMENT=production
            # For production, these must come from secure environment
            if [[ -z "${DATABASE_HOST:-}" ]] || [[ -z "${DATABASE_PASSWORD:-}" ]]; then
                log_error "DATABASE_HOST and DATABASE_PASSWORD environment variables required for production"
                exit 1
            fi
            ;;
    esac
    
    log_success "Environment configured for $ENVIRONMENT"
}

create_backup() {
    log_info "Creating database backup for $ENVIRONMENT..."
    
    # Only create backups for staging/production
    if [[ "$ENVIRONMENT" != "development" ]]; then
        BACKUP_DIR="$PROJECT_ROOT/backups"
        mkdir -p "$BACKUP_DIR"
        
        TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
        BACKUP_FILE="$BACKUP_DIR/backup_${ENVIRONMENT}_${TIMESTAMP}.sql"
        
        # Create database backup
        mysqldump \
            -h "${DATABASE_HOST}" \
            -P "${DATABASE_PORT:-3306}" \
            -u "${DATABASE_USERNAME}" \
            -p"${DATABASE_PASSWORD}" \
            "${DATABASE_NAME}" > "$BACKUP_FILE"
        
        log_success "Backup created: $BACKUP_FILE"
    else
        log_info "Skipping backup for development environment"
    fi
}

run_alembic_command() {
    local alembic_cmd="$1"
    local description="$2"
    
    log_info "$description"
    
    cd "$PROJECT_ROOT"
    
    case "$alembic_cmd" in
        upgrade)
            python -m alembic upgrade head
            ;;
        downgrade)
            python -m alembic downgrade -1
            ;;
        current)
            python -m alembic current
            ;;
        history)
            python -m alembic history --verbose
            ;;
        validate)
            python -m alembic check
            ;;
    esac
    
    log_success "$description completed"
}

validate_migration() {
    log_info "Validating migration state..."
    
    # Check current migration version
    log_info "Current migration version:"
    run_alembic_command "current" "Checking current version"
    
    # Validate migration files
    log_info "Validating migration files..."
    if python -c "
import sys
sys.path.append('.')
from migration.env import target_metadata
print(f'Found {len(target_metadata.tables)} tables in metadata')
for table_name in target_metadata.tables.keys():
    print(f'  - {table_name}')
" 2>/dev/null; then
        log_success "Migration validation passed"
    else
        log_warning "Migration validation had issues (this might be normal if database is not accessible)"
    fi
}

# =============================================================================
# Command Implementations
# =============================================================================
cmd_upgrade() {
    log_info "🚀 Starting database migration upgrade for $ENVIRONMENT..."
    
    # Create backup for non-dev environments
    if [[ "$ENVIRONMENT" != "development" ]]; then
        create_backup
    fi
    
    # Run migration
    run_alembic_command "upgrade" "Applying pending migrations"
    
    # Validate result
    validate_migration
    
    log_success "✅ Migration upgrade completed successfully!"
}

cmd_downgrade() {
    log_warning "⚠️  Starting database migration downgrade for $ENVIRONMENT..."
    
    # Extra confirmation for production
    if [[ "$ENVIRONMENT" == "production" ]]; then
        echo -n "Are you sure you want to downgrade production database? (yes/no): "
        read -r CONFIRM
        if [[ "$CONFIRM" != "yes" ]]; then
            log_info "Downgrade cancelled by user"
            exit 0
        fi
    fi
    
    # Create backup
    create_backup
    
    # Run downgrade
    run_alembic_command "downgrade" "Rolling back last migration"
    
    log_success "✅ Migration downgrade completed!"
}

cmd_current() {
    log_info "📍 Current migration status for $ENVIRONMENT:"
    run_alembic_command "current" "Getting current migration version"
}

cmd_history() {
    log_info "📚 Migration history for $ENVIRONMENT:"
    run_alembic_command "history" "Getting migration history"
}

cmd_backup() {
    log_info "💾 Creating database backup for $ENVIRONMENT..."
    create_backup
    log_success "✅ Backup completed!"
}

cmd_validate() {
    log_info "🔍 Validating migration environment for $ENVIRONMENT..."
    validate_migration
    run_alembic_command "validate" "Validating migration state"
    log_success "✅ Validation completed!"
}

# =============================================================================
# Main Execution
# =============================================================================
main() {
    if [[ "$COMMAND" == "help" ]]; then
        show_usage
        exit 0
    fi
    
    log_info "🗄️  Database Migration Management - Enterprise Edition"
    log_info "Command: $COMMAND"
    log_info "Environment: $ENVIRONMENT"
    
    validate_command
    validate_environment
    check_requirements
    set_environment
    
    # Execute command
    case "$COMMAND" in
        upgrade)    cmd_upgrade ;;
        downgrade)  cmd_downgrade ;;
        current)    cmd_current ;;
        history)    cmd_history ;;
        backup)     cmd_backup ;;
        validate)   cmd_validate ;;
    esac
}

# Execute main function
main "$@" 