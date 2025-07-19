#!/bin/bash
# =============================================================================
# Professional Deploy Script for AWS SAM
# =============================================================================
# 
# This script handles professional deployment to AWS using SAM CLI
# with environment-specific configuration and validation.
#
# Features:
# - Environment validation
# - AWS credentials check
# - Parameter validation
# - Clean deployment process
# - Post-deployment validation
#
# Usage: ./scripts/deploy.sh [environment] [aws-profile]
# Example: ./scripts/deploy.sh production accounting-prod
# =============================================================================

set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
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

check_requirements() {
    log_info "Checking deployment requirements..."
    
    # Check if SAM CLI is installed
    if ! command -v sam &> /dev/null; then
        log_error "SAM CLI is not installed. Please install SAM CLI first."
        exit 1
    fi
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install AWS CLI first."
        exit 1
    fi
    
    # Check if template.yaml exists
    if [[ ! -f "$PROJECT_ROOT/template.yaml" ]]; then
        log_error "template.yaml not found in project root."
        exit 1
    fi
    
    log_success "All requirements satisfied"
}

validate_environment() {
    log_info "Validating environment: $ENVIRONMENT"
    
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

validate_aws_credentials() {
    log_info "Validating AWS credentials for profile: $AWS_PROFILE"
    
    # Set AWS profile
    export AWS_PROFILE="$AWS_PROFILE"
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "Invalid AWS credentials for profile: $AWS_PROFILE"
        log_error "Please configure your AWS credentials first."
        exit 1
    fi
    
    # Get account info
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    REGION=$(aws configure get region)
    
    log_success "AWS credentials validated"
    log_info "Account ID: $ACCOUNT_ID"
    log_info "Region: $REGION"
}

check_build() {
    log_info "Checking build artifacts..."
    
    if [[ ! -d "$PROJECT_ROOT/package" ]]; then
        log_warning "Build not found. Running build first..."
        "$SCRIPT_DIR/build.sh" "$ENVIRONMENT"
    else
        log_success "Build artifacts found"
    fi
}

deploy_infrastructure() {
    log_info "Deploying infrastructure with SAM..."
    
    cd "$PROJECT_ROOT"
    
    # SAM build (validates template)
    log_info "Building SAM application..."
    sam build --use-container
    
    # SAM deploy
    log_info "Deploying to AWS..."
    sam deploy \
        --stack-name "accounting-app-$ENVIRONMENT" \
        --parameter-overrides \
            Environment="$ENVIRONMENT" \
        --capabilities CAPABILITY_IAM \
        --region "$REGION" \
        --confirm-changeset \
        --fail-on-empty-changeset false
    
    log_success "Infrastructure deployed successfully"
}

get_outputs() {
    log_info "Retrieving stack outputs..."
    
    STACK_NAME="accounting-app-$ENVIRONMENT"
    
    # Get API URL
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
        --output text)
    
    # Get Function Name
    FUNCTION_NAME=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`FunctionName`].OutputValue' \
        --output text)
    
    log_success "Stack outputs retrieved"
    echo ""
    echo "📍 Deployment Information:"
    echo "   Environment: $ENVIRONMENT"
    echo "   Stack Name: $STACK_NAME"
    echo "   API URL: $API_URL"
    echo "   Function Name: $FUNCTION_NAME"
    echo ""
}

validate_deployment() {
    log_info "Validating deployment..."
    
    # Health check
    if [[ -n "${API_URL:-}" ]]; then
        log_info "Testing API health check..."
        
        HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/health" || echo "000")
        
        if [[ "$HTTP_STATUS" == "200" ]]; then
            log_success "API health check passed"
        else
            log_warning "API health check failed (HTTP $HTTP_STATUS)"
            log_info "This might be normal if the database is not accessible"
        fi
    fi
    
    log_success "Deployment validation completed"
}

# =============================================================================
# Main Execution
# =============================================================================
main() {
    log_info "🚀 Starting professional deployment to AWS..."
    log_info "Environment: $ENVIRONMENT"
    log_info "AWS Profile: $AWS_PROFILE"
    log_info "Project: $(basename "$PROJECT_ROOT")"
    
    check_requirements
    validate_environment
    validate_aws_credentials
    check_build
    deploy_infrastructure
    get_outputs
    validate_deployment
    
    log_success "✅ Deployment completed successfully!"
    log_info "🌐 API is available at: $API_URL"
}

# Execute main function
main "$@" 