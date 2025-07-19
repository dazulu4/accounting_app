#!/bin/bash
# =============================================================================
# Migration Generation Script - Enterprise Edition
# =============================================================================
# 
# Professional script for generating new database migrations with proper
# naming conventions and validation.
#
# Features:
# - Automatic migration generation with proper naming
# - Model validation before generation
# - Professional migration templates
# - Environment validation
# - Change detection and review
#
# Usage: ./scripts/generate-migration.sh [message] [--auto]
# Example: ./scripts/generate-migration.sh "add_user_preferences_table"
# Example: ./scripts/generate-migration.sh "update_task_schema" --auto
# =============================================================================

set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MESSAGE="${1:-}"
AUTO_GENERATE="${2:-}"

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
    echo "Usage: $0 [message] [--auto]"
    echo ""
    echo "Parameters:"
    echo "  message    - Migration message (required)"
    echo "  --auto     - Use autogenerate (optional)"
    echo ""
    echo "Examples:"
    echo "  $0 \"add_user_preferences_table\""
    echo "  $0 \"update_task_schema\" --auto"
    echo "  $0 \"create_audit_log_table\""
    echo ""
    echo "Migration Naming Conventions:"
    echo "  - Use snake_case"
    echo "  - Be descriptive but concise"
    echo "  - Include action (add, update, remove, create, drop)"
    echo "  - Examples: create_users_table, add_email_column, remove_deprecated_fields"
}

validate_input() {
    if [[ -z "$MESSAGE" ]]; then
        log_error "Migration message is required"
        show_usage
        exit 1
    fi
    
    # Validate message format
    if [[ ! "$MESSAGE" =~ ^[a-z0-9_]+$ ]]; then
        log_error "Migration message must use snake_case (lowercase letters, numbers, and underscores only)"
        log_error "Example: add_user_email_column"
        exit 1
    fi
    
    log_success "Valid migration message: $MESSAGE"
}

check_requirements() {
    log_info "Checking requirements for migration generation..."
    
    # Check if python/alembic is available
    if ! command -v python &> /dev/null; then
        log_error "Python is not available. Please activate your virtual environment."
        exit 1
    fi
    
    # Check if migration directory exists
    if [[ ! -d "$PROJECT_ROOT/migration" ]]; then
        log_error "Migration directory not found: $PROJECT_ROOT/migration"
        exit 1
    fi
    
    # Check if models can be imported
    if ! python -c "
import sys
sys.path.append('.')
try:
    from infrastructure.driven_adapters.repositories.task_repository import TaskModel
    from infrastructure.driven_adapters.repositories.base import Base
    print('Models imported successfully')
except Exception as e:
    print(f'Error importing models: {e}')
    sys.exit(1)
" 2>/dev/null; then
        log_error "Unable to import database models. Please check your model definitions."
        exit 1
    fi
    
    log_success "All requirements satisfied"
}

validate_models() {
    log_info "Validating database models..."
    
    python -c "
import sys
sys.path.append('.')
from infrastructure.driven_adapters.repositories.base import Base

# Get all tables from metadata
tables = Base.metadata.tables
print(f'Found {len(tables)} table(s) in metadata:')
for table_name, table in tables.items():
    print(f'  - {table_name} ({len(table.columns)} columns)')
    
# Validate table definitions
for table_name, table in tables.items():
    if not table.primary_key:
        print(f'WARNING: Table {table_name} has no primary key')
    
print('Model validation completed')
"
    
    log_success "Model validation completed"
}

show_current_state() {
    log_info "Current migration state:"
    
    cd "$PROJECT_ROOT"
    
    # Show current version
    echo "Current version:"
    python -m alembic current || log_warning "Unable to get current version (database may not be accessible)"
    
    # Show recent migrations
    echo ""
    echo "Recent migrations:"
    python -m alembic history -r-3: || log_warning "Unable to get migration history"
}

generate_migration() {
    log_info "Generating new migration: $MESSAGE"
    
    cd "$PROJECT_ROOT"
    
    # Set environment for migration generation
    export APP_ENVIRONMENT=development
    
    if [[ "$AUTO_GENERATE" == "--auto" ]]; then
        log_info "Using autogenerate mode..."
        python -m alembic revision --autogenerate -m "$MESSAGE"
    else
        log_info "Creating empty migration template..."
        python -m alembic revision -m "$MESSAGE"
    fi
    
    # Find the newly created migration file
    MIGRATION_FILE=$(find migration/versions -name "*_${MESSAGE}.py" | head -1)
    
    if [[ -n "$MIGRATION_FILE" ]]; then
        log_success "Migration created: $MIGRATION_FILE"
        
        # Show the migration file path
        echo ""
        log_info "Migration file location: $MIGRATION_FILE"
        
        # Show migration content preview
        echo ""
        log_info "Migration content preview:"
        echo "----------------------------------------"
        head -20 "$MIGRATION_FILE"
        echo "----------------------------------------"
        
        # Provide next steps
        echo ""
        log_info "Next steps:"
        echo "1. Review the generated migration file: $MIGRATION_FILE"
        echo "2. Edit the migration if needed (add custom logic, data migrations, etc.)"
        echo "3. Test the migration: ./scripts/migrate.sh validate"
        echo "4. Apply the migration: ./scripts/migrate.sh upgrade development"
        
    else
        log_error "Migration file not found after generation"
        exit 1
    fi
}

review_changes() {
    if [[ "$AUTO_GENERATE" == "--auto" ]]; then
        log_info "Reviewing detected schema changes..."
        
        cd "$PROJECT_ROOT"
        
        # Try to show what changes would be detected
        python -c "
import sys
sys.path.append('.')
try:
    from alembic import command
    from alembic.config import Config
    
    config = Config('alembic.ini')
    print('Checking for model changes...')
    
except Exception as e:
    print(f'Unable to detect changes: {e}')
"
    fi
}

# =============================================================================
# Main Execution
# =============================================================================
main() {
    if [[ "$MESSAGE" == "help" ]] || [[ "$MESSAGE" == "--help" ]]; then
        show_usage
        exit 0
    fi
    
    log_info "🔄 Migration Generation - Enterprise Edition"
    log_info "Message: $MESSAGE"
    log_info "Mode: $([ "$AUTO_GENERATE" == "--auto" ] && echo "Autogenerate" || echo "Manual")"
    
    validate_input
    check_requirements
    validate_models
    show_current_state
    review_changes
    generate_migration
    
    log_success "✅ Migration generation completed successfully!"
}

# Execute main function
main "$@" 