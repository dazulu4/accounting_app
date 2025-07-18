#!/bin/bash

# Script de build para AWS SAM
# Este script prepara la aplicación para el despliegue en AWS Lambda

set -e

echo "🚀 Iniciando build de Accounting App para AWS SAM..."

# Variables
PROJECT_NAME="accounting-app"
BUILD_DIR=".aws-sam"
PACKAGE_DIR="package"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "template.yaml" ]; then
    print_error "No se encontró template.yaml. Ejecuta este script desde el directorio raíz del proyecto."
    exit 1
fi

# Verificar que Poetry está instalado
if ! command -v poetry &> /dev/null; then
    print_error "Poetry no está instalado. Instálalo primero."
    exit 1
fi

# Verificar que AWS SAM CLI está instalado
if ! command -v sam &> /dev/null; then
    print_warning "AWS SAM CLI no está instalado. Instálalo para hacer build local."
    print_warning "Puedes continuar para preparar los archivos."
fi

print_status "Limpiando directorios de build anteriores..."
rm -rf $BUILD_DIR
rm -rf $PACKAGE_DIR

print_status "Instalando dependencias con Poetry..."
poetry install --only main

print_status "Creando directorio de build..."
mkdir -p $BUILD_DIR
mkdir -p $PACKAGE_DIR

print_status "Copiando archivos de la aplicación..."
cp -r application/ $PACKAGE_DIR/
cp -r domain/ $PACKAGE_DIR/
cp -r infrastructure/ $PACKAGE_DIR/
cp -r migration/ $PACKAGE_DIR/

print_status "Copiando archivos de configuración..."
cp pyproject.toml $PACKAGE_DIR/
cp poetry.lock $PACKAGE_DIR/
cp alembic.ini $PACKAGE_DIR/
cp dummyusers.json $PACKAGE_DIR/

print_status "Creando requirements.txt para Lambda..."
cat > $PACKAGE_DIR/requirements.txt << 'EOF'
# Requirements para AWS Lambda
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
EOF

print_status "Optimizando dependencias para Lambda..."
cd $PACKAGE_DIR

# Crear archivo de configuración para Lambda
cat > lambda_config.py << EOF
"""
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
EOF

# Crear script de inicialización para Lambda
cat > lambda_init.py << EOF
"""
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
EOF

print_status "Creando archivo de configuración de despliegue..."
cat > samconfig.toml << EOF
version = 0.1
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
EOF

print_status "Creando script de despliegue..."
cat > deploy.sh << 'EOF'
#!/bin/bash

# Script de despliegue para AWS SAM
# Uso: ./deploy.sh [environment]

set -e

ENVIRONMENT=${1:-production}
STACK_NAME="accounting-app-${ENVIRONMENT}"

echo "🚀 Desplegando Accounting App en AWS SAM..."
echo "Environment: $ENVIRONMENT"
echo "Stack Name: $STACK_NAME"

# Verificar que AWS CLI está configurado
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI no está configurado. Ejecuta 'aws configure' primero."
    exit 1
fi

# Verificar que SAM CLI está instalado
if ! command -v sam &> /dev/null; then
    echo "❌ AWS SAM CLI no está instalado."
    exit 1
fi

# Build del proyecto
echo "📦 Construyendo proyecto..."
sam build

# Desplegar
echo "🚀 Desplegando stack..."
sam deploy \
    --stack-name $STACK_NAME \
    --parameter-overrides Environment=$ENVIRONMENT \
    --capabilities CAPABILITY_IAM \
    --no-confirm-changeset

echo "✅ Despliegue completado!"
echo "🔗 URL de la API: $(aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`AccountingApi`].OutputValue' --output text)"
EOF

chmod +x deploy.sh

print_status "Creando archivo .dockerignore..."
cat > .dockerignore << EOF
# Archivos de desarrollo
.git
.gitignore
README.md
Makefile
make.bat
.vscode
.pytest_cache
htmlcov
.coverage

# Archivos de testing
tests/
scripts/

# Archivos de build
.aws-sam/
package/

# Archivos de configuración local
.env
*.db
*.sqlite

# Logs
*.log

# Archivos temporales
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
EOF

print_status "Creando archivo de configuración para CI/CD..."
cat > .github/workflows/deploy.yml << 'EOF'
name: Deploy to AWS SAM

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install Poetry
      run: |
        curl -sSL https://install.python-poetry.org | python3 -
    
    - name: Install dependencies
      run: |
        poetry install
    
    - name: Run tests
      run: |
        poetry run pytest --cov=domain --cov=application --cov=infrastructure --cov-fail-under=70
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Install AWS SAM
      run: |
        curl -L https://github.com/aws/aws-sam-cli/releases/latest/download/sam-linux-x86_64.zip -o sam.zip
        unzip sam.zip -d sam-installation
        sudo ./sam-installation/install
    
    - name: Build and deploy
      run: |
        sam build
        sam deploy --no-confirm-changeset --capabilities CAPABILITY_IAM
EOF

cd ..

print_status "Creando documentación de despliegue..."
cat > DEPLOYMENT.md << 'EOF'
# Guía de Despliegue - Accounting App

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
./scripts/build.sh

# Ejecutar localmente
sam local start-api
```

### Despliegue a AWS
```bash
# Build y deploy
./scripts/build.sh
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
EOF

print_status "Creando archivo de configuración para variables de entorno..."
cat > .env.example << EOF
# Configuración de Base de Datos
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
EOF

print_status "Creando archivo de configuración para testing local..."
cat > samconfig.local.toml << EOF
version = 0.1
[default]
[default.local_start_api]
[default.local_start_api.parameters]
parameter_overrides = "Environment=development"
env_vars = "env.json"
EOF

print_status "Creando archivo de variables de entorno para testing..."
cat > env.json << EOF
{
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
EOF

print_status "✅ Build completado exitosamente!"
print_status "📁 Archivos generados en: $PACKAGE_DIR/"
print_status "📋 Próximos pasos:"
print_status "   1. Configurar variables de entorno en .env.example"
print_status "   2. Ejecutar: cd package && ./deploy.sh"
print_status "   3. Para testing local: sam local start-api"

echo ""
echo "🎯 Para hacer el despliegue real:"
echo "   1. Configurar AWS CLI: aws configure"
echo "   2. Instalar AWS SAM CLI"
echo "   3. Configurar base de datos RDS"
echo "   4. Ejecutar script de despliegue" 