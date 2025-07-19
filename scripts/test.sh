#!/bin/bash
# =============================================================================
# Test Execution Script - Enterprise Edition
# =============================================================================
# 
# Professional test execution script with support for different test types,
# coverage analysis, performance monitoring, and CI/CD integration.
#
# Features:
# - Test pyramid execution (unit/integration/e2e)
# - Coverage analysis and reporting
# - Performance benchmarking
# - Parallel test execution
# - CI/CD integration support
# - Quality gates enforcement
#
# Usage: ./scripts/test.sh [test-type] [options]
# Examples:
#   ./scripts/test.sh unit
#   ./scripts/test.sh integration --coverage
#   ./scripts/test.sh all --parallel --report
# =============================================================================

set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEST_TYPE="${1:-all}"
COVERAGE_ENABLED=false
PARALLEL_ENABLED=false
REPORT_ENABLED=false
PERFORMANCE_ENABLED=false
VERBOSE_ENABLED=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

log_header() {
    echo -e "${PURPLE}[TEST]${NC} $1"
}

show_usage() {
    echo "Usage: $0 [test-type] [options]"
    echo ""
    echo "Test Types:"
    echo "  unit        - Run unit tests only (fast)"
    echo "  integration - Run integration tests only"
    echo "  e2e         - Run end-to-end tests only (slow)"
    echo "  all         - Run all tests (default)"
    echo "  smoke       - Run smoke tests for quick validation"
    echo "  performance - Run performance tests only"
    echo ""
    echo "Options:"
    echo "  --coverage  - Enable coverage analysis"
    echo "  --parallel  - Enable parallel test execution"
    echo "  --report    - Generate comprehensive reports"
    echo "  --performance - Enable performance monitoring"
    echo "  --verbose   - Enable verbose output"
    echo "  --help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 unit --coverage"
    echo "  $0 integration --parallel"
    echo "  $0 all --coverage --report"
    echo "  $0 performance --verbose"
}

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --coverage)
                COVERAGE_ENABLED=true
                shift
                ;;
            --parallel)
                PARALLEL_ENABLED=true
                shift
                ;;
            --report)
                REPORT_ENABLED=true
                shift
                ;;
            --performance)
                PERFORMANCE_ENABLED=true
                shift
                ;;
            --verbose)
                VERBOSE_ENABLED=true
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                shift
                ;;
        esac
    done
}

check_requirements() {
    log_info "Checking test requirements..."
    
    # Check if pytest is available
    if ! command -v python &> /dev/null; then
        log_error "Python is not available. Please activate your virtual environment."
        exit 1
    fi
    
    # Check if required packages are installed
    if ! python -c "import pytest" 2>/dev/null; then
        log_error "pytest is not installed. Please install test dependencies."
        exit 1
    fi
    
    if [[ "$COVERAGE_ENABLED" == "true" ]] && ! python -c "import coverage" 2>/dev/null; then
        log_error "coverage is not installed. Please install coverage package."
        exit 1
    fi
    
    log_success "All requirements satisfied"
}

setup_test_environment() {
    log_info "Setting up test environment..."
    
    # Set test environment variables
    export APP_ENVIRONMENT=test
    export DATABASE_NAME=accounting_test
    export LOG_LEVEL=WARNING
    
    # Create necessary directories
    mkdir -p "$PROJECT_ROOT/htmlcov"
    mkdir -p "$PROJECT_ROOT/test-reports"
    
    log_success "Test environment configured"
}

build_pytest_command() {
    local test_pattern="$1"
    local cmd="python -m pytest"
    
    # Add test pattern
    if [[ "$test_pattern" != "all" ]]; then
        cmd="$cmd -m $test_pattern"
    fi
    
    # Add coverage options
    if [[ "$COVERAGE_ENABLED" == "true" ]]; then
        cmd="$cmd --cov=domain --cov=application --cov=infrastructure"
        cmd="$cmd --cov-report=html:htmlcov"
        cmd="$cmd --cov-report=xml:coverage.xml"
        cmd="$cmd --cov-report=term-missing"
        cmd="$cmd --cov-fail-under=85"
    fi
    
    # Add parallel execution
    if [[ "$PARALLEL_ENABLED" == "true" ]]; then
        cmd="$cmd -n auto"
    fi
    
    # Add verbosity
    if [[ "$VERBOSE_ENABLED" == "true" ]]; then
        cmd="$cmd -v -s"
    else
        cmd="$cmd --tb=short"
    fi
    
    # Add performance monitoring
    if [[ "$PERFORMANCE_ENABLED" == "true" ]]; then
        cmd="$cmd --durations=10"
    fi
    
    # Add reporting
    if [[ "$REPORT_ENABLED" == "true" ]]; then
        cmd="$cmd --junitxml=test-reports/junit.xml"
        cmd="$cmd --html=test-reports/report.html --self-contained-html"
    fi
    
    echo "$cmd"
}

run_tests() {
    local test_type="$1"
    
    log_header "Running $test_type tests..."
    
    cd "$PROJECT_ROOT"
    
    # Build and execute pytest command
    local pytest_cmd
    pytest_cmd=$(build_pytest_command "$test_type")
    
    log_info "Executing: $pytest_cmd"
    
    # Run tests with timing
    local start_time
    start_time=$(date +%s)
    
    if eval "$pytest_cmd"; then
        local end_time
        end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        log_success "$test_type tests completed successfully in ${duration}s"
        return 0
    else
        local end_time
        end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        log_error "$test_type tests failed after ${duration}s"
        return 1
    fi
}

generate_reports() {
    if [[ "$REPORT_ENABLED" == "true" ]]; then
        log_info "Generating comprehensive test reports..."
        
        # Coverage summary
        if [[ "$COVERAGE_ENABLED" == "true" ]] && [[ -f "coverage.xml" ]]; then
            log_info "Coverage report generated: htmlcov/index.html"
            
            # Print coverage summary
            python -c "
import xml.etree.ElementTree as ET
tree = ET.parse('coverage.xml')
root = tree.getroot()
line_rate = float(root.attrib['line-rate']) * 100
branch_rate = float(root.attrib['branch-rate']) * 100
print(f'Line Coverage: {line_rate:.2f}%')
print(f'Branch Coverage: {branch_rate:.2f}%')
"
        fi
        
        # Test summary
        if [[ -f "test-reports/junit.xml" ]]; then
            log_info "JUnit report generated: test-reports/junit.xml"
            log_info "HTML report generated: test-reports/report.html"
        fi
        
        log_success "All reports generated successfully"
    fi
}

show_summary() {
    local test_type="$1"
    local success="$2"
    
    echo ""
    echo "==============================================="
    echo "         TEST EXECUTION SUMMARY"
    echo "==============================================="
    echo "Test Type: $test_type"
    echo "Coverage: $([ "$COVERAGE_ENABLED" == "true" ] && echo "Enabled" || echo "Disabled")"
    echo "Parallel: $([ "$PARALLEL_ENABLED" == "true" ] && echo "Enabled" || echo "Disabled")"
    echo "Reports: $([ "$REPORT_ENABLED" == "true" ] && echo "Enabled" || echo "Disabled")"
    echo "Status: $([ "$success" == "0" ] && echo -e "${GREEN}PASSED${NC}" || echo -e "${RED}FAILED${NC}")"
    
    if [[ "$COVERAGE_ENABLED" == "true" && -f "htmlcov/index.html" ]]; then
        echo "Coverage Report: htmlcov/index.html"
    fi
    
    if [[ "$REPORT_ENABLED" == "true" && -f "test-reports/report.html" ]]; then
        echo "Test Report: test-reports/report.html"
    fi
    
    echo "==============================================="
}

# =============================================================================
# Test Type Implementations
# =============================================================================
run_unit_tests() {
    log_header "🧪 Running Unit Tests (Testing Pyramid: 80%)"
    run_tests "unit"
}

run_integration_tests() {
    log_header "🔗 Running Integration Tests (Testing Pyramid: 15%)"
    run_tests "integration"
}

run_e2e_tests() {
    log_header "🎯 Running End-to-End Tests (Testing Pyramid: 5%)"
    run_tests "e2e"
}

run_smoke_tests() {
    log_header "💨 Running Smoke Tests (Quick Validation)"
    run_tests "smoke"
}

run_performance_tests() {
    log_header "⚡ Running Performance Tests"
    PERFORMANCE_ENABLED=true
    run_tests "performance"
}

run_all_tests() {
    log_header "🚀 Running Complete Test Suite (Testing Pyramid)"
    
    local overall_success=0
    
    # Run in testing pyramid order
    log_info "Phase 1: Unit Tests (80% of test suite)"
    if ! run_unit_tests; then
        overall_success=1
        log_warning "Unit tests failed, but continuing with integration tests..."
    fi
    
    log_info "Phase 2: Integration Tests (15% of test suite)"
    if ! run_integration_tests; then
        overall_success=1
        log_warning "Integration tests failed, but continuing with E2E tests..."
    fi
    
    log_info "Phase 3: End-to-End Tests (5% of test suite)"
    if ! run_e2e_tests; then
        overall_success=1
        log_warning "E2E tests failed"
    fi
    
    return $overall_success
}

# =============================================================================
# Main Execution
# =============================================================================
main() {
    parse_arguments "$@"
    
    log_info "🧪 Test Execution - Enterprise Edition"
    log_info "Test Type: $TEST_TYPE"
    
    check_requirements
    setup_test_environment
    
    local test_result
    
    case "$TEST_TYPE" in
        unit)
            run_unit_tests
            test_result=$?
            ;;
        integration)
            run_integration_tests
            test_result=$?
            ;;
        e2e)
            run_e2e_tests
            test_result=$?
            ;;
        smoke)
            run_smoke_tests
            test_result=$?
            ;;
        performance)
            run_performance_tests
            test_result=$?
            ;;
        all)
            run_all_tests
            test_result=$?
            ;;
        *)
            log_error "Invalid test type: $TEST_TYPE"
            show_usage
            exit 1
            ;;
    esac
    
    generate_reports
    show_summary "$TEST_TYPE" "$test_result"
    
    exit $test_result
}

# Execute main function
main "$@" 