#!/usr/bin/env python3
"""
Script de build para AWS SAM
Este script automatiza el proceso de preparación para el despliegue en AWS Lambda
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any

# Configuración
PROJECT_ROOT = Path(__file__).parent.parent
BUILD_DIR = PROJECT_ROOT / ".aws-sam"
PACKAGE_DIR = PROJECT_ROOT / "package"
TEMPLATE_FILE = PROJECT_ROOT / "template.yaml"

# Directorios a copiar
DIRECTORIES_TO_COPY = [
    "application",
    "domain", 
    "infrastructure",
    "migration"
]

# Archivos a copiar
FILES_TO_COPY = [
    "pyproject.toml",
    "poetry.lock",
    "alembic.ini",
    "dummyusers.json"
]

def print_status(message: str) -> None:
    """Imprimir mensaje de estado"""
    print(f"🚀 {message}")

def print_error(message: str) -> None:
    """Imprimir mensaje de error"""
    print(f"❌ {message}")

def print_success(message: str) -> None:
    """Imprimir mensaje de éxito"""
    print(f"✅ {message}")

def check_prerequisites() -> bool:
    """Verificar prerrequisitos"""
    print_status("Verificando prerrequisitos...")
    
    # Verificar que estamos en el directorio correcto
    if not TEMPLATE_FILE.exists():
        print_error("No se encontró template.yaml. Ejecuta este script desde el directorio raíz del proyecto.")
        return False
    
    # Verificar que Poetry está instalado
    try:
        subprocess.run(["poetry", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Poetry no está instalado. Instálalo primero.")
        return False
    
    print_success("Prerrequisitos verificados")
    return True

def clean_build_directories() -> None:
    """Limpiar directorios de build anteriores"""
    print_status("Limpiando directorios de build anteriores...")
    
    for directory in [BUILD_DIR, PACKAGE_DIR]:
        if directory.exists():
            shutil.rmtree(directory)
    
    print_success("Directorios limpiados")

def install_dependencies() -> bool:
    """Instalar dependencias con Poetry"""
    print_status("Instalando dependencias con Poetry...")
    
    try:
        subprocess.run(["poetry", "install", "--only", "main"], check=True, cwd=PROJECT_ROOT)
        print_success("Dependencias instaladas")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Error instalando dependencias: {e}")
        return False

def create_build_directories() -> None:
    """Crear directorios de build"""
    print_status("Creando directorios de build...")
    
    BUILD_DIR.mkdir(exist_ok=True)
    PACKAGE_DIR.mkdir(exist_ok=True)
    
    print_success("Directorios creados")

def copy_application_files() -> None:
    """Copiar archivos de la aplicación"""
    print_status("Copiando archivos de la aplicación...")
    
    for directory in DIRECTORIES_TO_COPY:
        src = PROJECT_ROOT / directory
        dst = PACKAGE_DIR / directory
        
        if src.exists():
            shutil.copytree(src, dst)
            print(f"  📁 Copiado: {directory}")
    
    for file in FILES_TO_COPY:
        src = PROJECT_ROOT / file
        dst = PACKAGE_DIR / file
        
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  📄 Copiado: {file}")
    
    print_success("Archivos de aplicación copiados")

def create_requirements_txt() -> bool:
    """Crear requirements.txt para Lambda"""
    print_status("Creando requirements.txt para Lambda...")
    
    try:
        # Crear requirements.txt manualmente basado en pyproject.toml
        requirements_content = """# Requirements para AWS Lambda
# Generado automáticamente por build script

# Framework web
flask==3.1.1
flask-cors==6.0.1

# Base de datos
sqlalchemy[asyncio]==2.0.41
aiomysql==0.2.0
pymysql==1.1.1
databases==0.9.0

# Migraciones
alembic==1.16.4

# Validación de datos
pydantic==2.11.7
pydantic-settings==2.10.1

# Utilidades
requests==2.32.4

# Testing (solo para desarrollo local)
pytest==8.4.1
pytest-asyncio==1.1.0
pytest-cov==4.1.0
pytest-mock==3.12.0
"""
        
        with open(PACKAGE_DIR / "requirements.txt", "w") as f:
            f.write(requirements_content)
        
        print_success("requirements.txt creado")
        return True
    except Exception as e:
        print_error(f"Error creando requirements.txt: {e}")
        return False

def create_lambda_config() -> None:
    """Crear archivos de configuración para Lambda"""
    print_status("Creando archivos de configuración para Lambda...")
    
    # Configuración de Lambda
    lambda_config = '''"""
Configuración específica para AWS Lambda
"""
import os

# Configuración de base de datos para Lambda
DATABASE_CONFIG = {
    'host': os.environ.get('DATABASE_HOST', 'localhost'),
    'port': int(os.environ.get('DATABASE_PORT', '3306')),
    'database': os.environ.get('DATABASE_NAME', 'accounting'),
    'user': os.environ.get('DATABASE_USER', 'admin'),
    'password': os.environ.get('DATABASE_PASSWORD', 'admin'),
}

# Configuración de logging para Lambda
LOGGING_CONFIG = {
    'level': os.environ.get('LOG_LEVEL', 'INFO'),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# Configuración de la aplicación
APP_CONFIG = {
    'environment': os.environ.get('ENVIRONMENT', 'production'),
    'version': '1.0.0'
}
'''
    
    with open(PACKAGE_DIR / "lambda_config.py", "w") as f:
        f.write(lambda_config)
    
    # Script de inicialización
    lambda_init = '''"""
Script de inicialización para AWS Lambda
"""
import os
import sys
import logging

# Configurar logging
logging.basicConfig(
    level=getattr(logging, os.environ.get('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def init_lambda():
    """Inicializar la aplicación para Lambda"""
    try:
        logger.info("Inicializando Accounting App en AWS Lambda...")
        
        # Verificar variables de entorno críticas
        required_env_vars = ['DATABASE_HOST', 'DATABASE_NAME', 'DATABASE_USER', 'DATABASE_PASSWORD']
        missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
        
        if missing_vars:
            logger.warning(f"Variables de entorno faltantes: {missing_vars}")
        
        logger.info("Inicialización completada")
        
    except Exception as e:
        logger.error(f"Error en inicialización: {str(e)}")
        raise

if __name__ == "__main__":
    init_lambda()
'''
    
    with open(PACKAGE_DIR / "lambda_init.py", "w") as f:
        f.write(lambda_init)
    
    print_success("Archivos de configuración creados")

def create_deployment_files() -> None:
    """Crear archivos de despliegue"""
    print_status("Creando archivos de despliegue...")
    
    # samconfig.toml
    samconfig = '''version = 0.1
[default]
[default.deploy]
[default.deploy.parameters]
stack_name = "accounting-app"
s3_bucket = "aws-sam-cli-managed-default-samclisourcebucket-XXXXXXXXXXXX"
s3_prefix = "accounting-app"
region = "us-east-1"
confirm_changeset = true
capabilities = "CAPABILITY_IAM"
parameter_overrides = "Environment=production"
image_repositories = []
'''
    
    with open(PACKAGE_DIR / "samconfig.toml", "w") as f:
        f.write(samconfig)
    
    # deploy.sh
    deploy_script = '''#!/bin/bash

# Script de despliegue para AWS SAM
# Uso: ./deploy.sh [environment]

set -e

ENVIRONMENT=${1:-production}
STACK_NAME="accounting-app-${ENVIRONMENT}"

echo "Desplegando Accounting App en AWS SAM..."
echo "Environment: $ENVIRONMENT"
echo "Stack Name: $STACK_NAME"

# Verificar que AWS CLI está configurado
if ! aws sts get-caller-identity &> /dev/null; then
    echo "ERROR: AWS CLI no está configurado. Ejecuta 'aws configure' primero."
    exit 1
fi

# Verificar que SAM CLI está instalado
if ! command -v sam &> /dev/null; then
    echo "ERROR: AWS SAM CLI no está instalado."
    exit 1
fi

# Build del proyecto
echo "Construyendo proyecto..."
sam build

# Desplegar
echo "Desplegando stack..."
sam deploy \\
    --stack-name $STACK_NAME \\
    --parameter-overrides Environment=$ENVIRONMENT \\
    --capabilities CAPABILITY_IAM \\
    --no-confirm-changeset

echo "Despliegue completado!"
echo "URL de la API: $(aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`AccountingApi`].OutputValue' --output text)"
'''
    
    with open(PACKAGE_DIR / "deploy.sh", "w") as f:
        f.write(deploy_script)
    
    # Hacer ejecutable el script
    os.chmod(PACKAGE_DIR / "deploy.sh", 0o755)
    
    print_success("Archivos de despliegue creados")

def create_env_files() -> None:
    """Crear archivos de variables de entorno"""
    print_status("Creando archivos de variables de entorno...")
    
    # .env.example
    env_example = '''# Configuración de Base de Datos
DATABASE_HOST=your-rds-endpoint.region.rds.amazonaws.com
DATABASE_PORT=3306
DATABASE_NAME=accounting
DATABASE_USER=admin
DATABASE_PASSWORD=your-secure-password

# Configuración de la Aplicación
ENVIRONMENT=production
LOG_LEVEL=INFO

# Configuración de AWS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
'''
    
    with open(PACKAGE_DIR / ".env.example", "w") as f:
        f.write(env_example)
    
    # env.json para testing local
    env_json = {
        "AccountingApiFunction": {
            "DATABASE_HOST": "localhost",
            "DATABASE_PORT": "3306",
            "DATABASE_NAME": "accounting",
            "DATABASE_USER": "admin",
            "DATABASE_PASSWORD": "admin",
            "ENVIRONMENT": "development",
            "LOG_LEVEL": "DEBUG"
        }
    }
    
    with open(PACKAGE_DIR / "env.json", "w") as f:
        json.dump(env_json, f, indent=2)
    
    print_success("Archivos de variables de entorno creados")

def create_documentation() -> None:
    """Crear documentación de despliegue"""
    print_status("Creando documentación de despliegue...")
    
    deployment_doc = '''# Guía de Despliegue - Accounting App

## Prerrequisitos

1. **AWS CLI** instalado y configurado
2. **AWS SAM CLI** instalado
3. **Poetry** instalado
4. **Python 3.11** instalado

## Configuración

### 1. Configurar AWS CLI
```bash
aws configure
```

### 2. Instalar dependencias
```bash
poetry install
```

## Despliegue

### Despliegue Local (Testing)
```bash
# Build local
python scripts/build.py

# Ejecutar localmente
sam local start-api
```

### Despliegue a AWS
```bash
# Build y deploy
python scripts/build.py
cd package
./deploy.sh production
```

## Configuración de Base de Datos

### Opción 1: RDS MySQL (Recomendado)
1. Crear instancia RDS MySQL en AWS
2. Configurar Security Groups
3. Actualizar variables de entorno en template.yaml

### Opción 2: Aurora Serverless
1. Crear cluster Aurora Serverless
2. Configurar conexiones VPC
3. Actualizar configuración de red

## Monitoreo

### CloudWatch Logs
- Logs de Lambda: `/aws/lambda/accounting-app-function`
- Métricas de API Gateway
- Métricas de RDS

### Alertas Recomendadas
- Error rate > 5%
- Latencia > 5 segundos
- Memory usage > 80%

## Troubleshooting

### Cold Starts
- Optimizar dependencias
- Usar Lambda Layers
- Configurar Provisioned Concurrency

### Errores de Conexión a BD
- Verificar Security Groups
- Verificar credenciales
- Verificar configuración de red

## Costos Estimados

### Lambda
- 1M requests/mes: ~$0.20
- 400,000 GB-segundos: ~$6.67

### API Gateway
- 1M requests/mes: ~$3.50

### RDS MySQL
- db.t3.micro: ~$15/mes

**Total estimado: ~$25/mes**
'''
    
    with open(PACKAGE_DIR / "DEPLOYMENT.md", "w") as f:
        f.write(deployment_doc)
    
    print_success("Documentación creada")

def main() -> int:
    """Función principal"""
    print("🚀 Iniciando build de Accounting App para AWS SAM...")
    
    try:
        # Verificar prerrequisitos
        if not check_prerequisites():
            return 1
        
        # Limpiar directorios
        clean_build_directories()
        
        # Instalar dependencias
        if not install_dependencies():
            return 1
        
        # Crear directorios
        create_build_directories()
        
        # Copiar archivos
        copy_application_files()
        
        # Crear requirements.txt
        if not create_requirements_txt():
            return 1
        
        # Crear archivos de configuración
        create_lambda_config()
        
        # Crear archivos de despliegue
        create_deployment_files()
        
        # Crear archivos de entorno
        create_env_files()
        
        # Crear documentación
        create_documentation()
        
        print_success("Build completado exitosamente!")
        print(f"📁 Archivos generados en: {PACKAGE_DIR}")
        print("📋 Próximos pasos:")
        print("   1. Configurar variables de entorno en .env.example")
        print("   2. Ejecutar: cd package && ./deploy.sh")
        print("   3. Para testing local: sam local start-api")
        
        return 0
        
    except Exception as e:
        print_error(f"Error durante el build: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 