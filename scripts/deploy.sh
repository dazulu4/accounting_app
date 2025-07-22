#!/bin/bash
# =============================================================================
# Despliegue a AWS SAM - Edición Simplificada
# =============================================================================
# 
# Este script unificado maneja todo el proceso de despliegue usando perfiles
# de samconfig.toml.
#
# Uso:
#   ./scripts/deploy.sh [entorno]
#
# Entornos:
#   - development (por defecto)
#   - production
#
# Ejemplo:
#   ./scripts/deploy.sh production
# =============================================================================

set -euo pipefail

# --- Configuración ---
ENVIRONMENT="${1:-development}"

# Colores para la salida
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # Sin Color

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

# --- Validación de Prerrequisitos ---
check_prerequisites() {
    log_info "Verificando prerrequisitos..."
    if ! command -v sam &> /dev/null; then
        log_error "AWS SAM CLI no está instalado. Por favor, instálalo."
        exit 1
    fi
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI no está instalado. Por favor, instálalo."
        exit 1
    fi
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "No se han configurado las credenciales de AWS. Por favor, ejecuta 'aws configure'."
        exit 1
    fi
    log_success "Prerrequisitos verificados."
}

# --- Lógica Principal ---
main() {
    log_info "🚀 Iniciando despliegue para el entorno: $ENVIRONMENT"

    check_prerequisites

    # --- Paso 1: Construcción del Paquete ---
    log_info "Paso 1: Construyendo el paquete de la aplicación con 'sam build'..."
    # Usamos --use-container para asegurar un entorno de build consistente
    if sam build --use-container; then
        log_success "Construcción del paquete completada."
    else
        log_error "La construcción del paquete falló."
        exit 1
    fi
    
    # --- Paso 2: Despliegue a AWS ---
    log_info "Paso 2: Desplegando la aplicación a AWS usando el perfil '$ENVIRONMENT'..."
    
    if sam deploy --config-env "$ENVIRONMENT"; then
        log_success "🎉 ¡Despliegue completado exitosamente para el entorno '$ENVIRONMENT'!"
        
        STACK_NAME="accounting-app-$ENVIRONMENT"
        AWS_REGION=$(aws configure get region)
        API_URL=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text --region "$AWS_REGION" 2>/dev/null)
        
        if [ -n "$API_URL" ]; then
            log_info "API Gateway URL: $API_URL"
        fi
    else
        log_error "El despliegue a AWS falló."
        exit 1
    fi
}

# --- Ejecución ---
main "$@" 