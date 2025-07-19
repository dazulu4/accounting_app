#!/bin/bash
# =============================================================================
# Professional Build Script for AWS Lambda Deployment
# =============================================================================
# 
# This script creates a clean, optimized build for AWS Lambda deployment
# following enterprise best practices for Python applications.
#
# Features:
# - Clean build environment
# - Optimized dependencies
# - Proper directory structure
# - Size optimization
# - Build validation
#
# Usage: ./scripts/build.sh [environment]
# Example: ./scripts/build.sh production
# =============================================================================

set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_ROOT/package"
ENVIRONMENT="${1:-development}"

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
    log_info "Checking build requirements..."
    
    # Check if poetry is installed
    if ! command -v poetry &> /dev/null; then
        log_error "Poetry is not installed. Please install Poetry first."
        exit 1
    fi
    
    # Check if pyproject.toml exists
    if [[ ! -f "$PROJECT_ROOT/pyproject.toml" ]]; then
        log_error "pyproject.toml not found in project root."
        exit 1
    fi
    
    log_success "All requirements satisfied"
}

clean_build() {
    log_info "Cleaning previous builds..."
    
    # Remove existing build directories
    rm -rf "$BUILD_DIR"
    rm -rf "$PROJECT_ROOT/.aws-sam/build"
    rm -rf "$PROJECT_ROOT/dist"
    
    log_success "Build environment cleaned"
}

create_build_structure() {
    log_info "Creating build directory structure..."
    
    mkdir -p "$BUILD_DIR"
    
    log_success "Build structure created"
}

copy_source_code() {
    log_info "Copying source code..."
    
    # Copy application source
    cp -r "$PROJECT_ROOT/application" "$BUILD_DIR/"
    cp -r "$PROJECT_ROOT/domain" "$BUILD_DIR/"
    cp -r "$PROJECT_ROOT/infrastructure" "$BUILD_DIR/"
    
    # Copy configuration files if they exist
    if [[ -f "$PROJECT_ROOT/alembic.ini" ]]; then
        cp "$PROJECT_ROOT/alembic.ini" "$BUILD_DIR/"
    fi
    
    log_success "Source code copied"
}

install_dependencies() {
    log_info "Installing production dependencies..."
    
    cd "$PROJECT_ROOT"
    
    # Export requirements without dev dependencies
    poetry export -f requirements.txt --output "$BUILD_DIR/requirements.txt" --without-hashes --only main
    
    # Install dependencies to build directory
    pip install -r "$BUILD_DIR/requirements.txt" -t "$BUILD_DIR" --no-deps --quiet
    
    log_success "Dependencies installed"
}

optimize_build() {
    log_info "Optimizing build size..."
    
    cd "$BUILD_DIR"
    
    # Remove unnecessary files
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.dist-info" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "tests" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "test" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.so" -delete 2>/dev/null || true
    
    # Remove documentation and examples
    find . -name "docs" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "examples" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.md" -delete 2>/dev/null || true
    find . -name "LICENSE*" -delete 2>/dev/null || true
    
    # Remove development tools
    rm -rf boto3* 2>/dev/null || true
    rm -rf botocore* 2>/dev/null || true
    rm -rf awscli* 2>/dev/null || true
    
    log_success "Build optimized"
}

validate_build() {
    log_info "Validating build..."
    
    # Check if main application files exist
    if [[ ! -f "$BUILD_DIR/application/lambda_handler.py" ]]; then
        log_error "Lambda handler not found in build"
        exit 1
    fi
    
    if [[ ! -f "$BUILD_DIR/application/main.py" ]]; then
        log_error "Main application not found in build"
        exit 1
    fi
    
    # Check build size
    BUILD_SIZE=$(du -sh "$BUILD_DIR" | cut -f1)
    log_info "Build size: $BUILD_SIZE"
    
    # Warn if build is too large
    BUILD_SIZE_MB=$(du -sm "$BUILD_DIR" | cut -f1)
    if [[ $BUILD_SIZE_MB -gt 250 ]]; then
        log_warning "Build size ($BUILD_SIZE) is large. Consider optimization."
    fi
    
    log_success "Build validation completed"
}

# =============================================================================
# Main Execution
# =============================================================================
main() {
    log_info "🏗️  Starting professional build for AWS Lambda..."
    log_info "Environment: $ENVIRONMENT"
    log_info "Project: $(basename "$PROJECT_ROOT")"
    
    check_requirements
    clean_build
    create_build_structure
    copy_source_code
    install_dependencies
    optimize_build
    validate_build
    
    log_success "✅ Build completed successfully!"
    log_info "📍 Build output: $BUILD_DIR"
    log_info "🚀 Ready for deployment with: sam deploy --parameter-overrides Environment=$ENVIRONMENT"
}

# Execute main function
main "$@" 