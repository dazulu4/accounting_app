#!/bin/bash
# =============================================================================
# AWS Parameters Setup Script
# =============================================================================
# 
# This script sets up AWS SSM Parameters and Secrets Manager entries
# for the accounting application across different environments.
#
# Usage: ./scripts/setup-aws-parameters.sh [environment] [aws-profile]
# Example: ./scripts/setup-aws-parameters.sh production accounting-prod
# =============================================================================

set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================
ENVIRONMENT="${1:-development}"
AWS_PROFILE="${2:-default}"

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

validate_environment() {
    case "$ENVIRONMENT" in
        development|staging|production)
            log_success "Valid environment: $ENVIRONMENT"
            ;;
        *)
            log_error "Invalid environment: $ENVIRONMENT. Must be development, staging, or production."
            exit 1
            ;;
    esac
}

setup_ssm_parameters() {
    log_info "Setting up SSM Parameters for $ENVIRONMENT..."
    
    # Set AWS profile
    export AWS_PROFILE="$AWS_PROFILE"
    
    # Database configuration parameters
    case "$ENVIRONMENT" in
        development)
            DB_HOST="localhost"
            DB_NAME="accounting_dev"
            DB_USERNAME="admin"
            ;;
        staging)
            DB_HOST="accounting-staging.cluster-xxx.us-east-1.rds.amazonaws.com"
            DB_NAME="accounting_staging"
            DB_USERNAME="admin"
            ;;
        production)
            DB_HOST="accounting-prod.cluster-xxx.us-east-1.rds.amazonaws.com"
            DB_NAME="accounting_prod"
            DB_USERNAME="admin"
            ;;
    esac
    
    # Create SSM Parameters
    aws ssm put-parameter \
        --name "/accounting-app/$ENVIRONMENT/database/host" \
        --value "$DB_HOST" \
        --type "String" \
        --description "Database host for $ENVIRONMENT environment" \
        --overwrite || log_warning "Parameter may already exist"
    
    aws ssm put-parameter \
        --name "/accounting-app/$ENVIRONMENT/database/name" \
        --value "$DB_NAME" \
        --type "String" \
        --description "Database name for $ENVIRONMENT environment" \
        --overwrite || log_warning "Parameter may already exist"
    
    aws ssm put-parameter \
        --name "/accounting-app/$ENVIRONMENT/database/username" \
        --value "$DB_USERNAME" \
        --type "String" \
        --description "Database username for $ENVIRONMENT environment" \
        --overwrite || log_warning "Parameter may already exist"
    
    log_success "SSM Parameters created successfully"
}

setup_secrets() {
    log_info "Setting up Secrets Manager entries for $ENVIRONMENT..."
    
    # Database password secret
    SECRET_NAME="accounting-app/$ENVIRONMENT/database/password"
    
    # Generate or prompt for password
    if [[ "$ENVIRONMENT" == "development" ]]; then
        DB_PASSWORD="admin123"
    else
        echo -n "Enter database password for $ENVIRONMENT: "
        read -s DB_PASSWORD
        echo ""
    fi
    
    # Create secret
    aws secretsmanager create-secret \
        --name "$SECRET_NAME" \
        --description "Database password for accounting app $ENVIRONMENT environment" \
        --secret-string "{\"password\":\"$DB_PASSWORD\"}" \
        2>/dev/null || {
            log_warning "Secret may already exist, updating..."
            aws secretsmanager update-secret \
                --secret-id "$SECRET_NAME" \
                --secret-string "{\"password\":\"$DB_PASSWORD\"}"
        }
    
    log_success "Secrets Manager entries created successfully"
}

verify_setup() {
    log_info "Verifying AWS parameter setup..."
    
    # Verify SSM Parameters
    aws ssm get-parameter --name "/accounting-app/$ENVIRONMENT/database/host" --query "Parameter.Value" --output text
    aws ssm get-parameter --name "/accounting-app/$ENVIRONMENT/database/name" --query "Parameter.Value" --output text
    aws ssm get-parameter --name "/accounting-app/$ENVIRONMENT/database/username" --query "Parameter.Value" --output text
    
    # Verify Secrets (without showing the value)
    aws secretsmanager describe-secret --secret-id "accounting-app/$ENVIRONMENT/database/password" --query "Name" --output text
    
    log_success "All parameters verified successfully"
}

# =============================================================================
# Main Execution
# =============================================================================
main() {
    log_info "🔧 Setting up AWS parameters for accounting application..."
    log_info "Environment: $ENVIRONMENT"
    log_info "AWS Profile: $AWS_PROFILE"
    
    validate_environment
    setup_ssm_parameters
    setup_secrets
    verify_setup
    
    log_success "✅ AWS parameters setup completed successfully!"
    log_info "You can now deploy the application with: ./scripts/deploy.sh $ENVIRONMENT $AWS_PROFILE"
}

# Execute main function
main "$@" 