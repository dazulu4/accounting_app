# 🚀 Fase 6: AWS SAM para Serverless - Accounting App

## 📋 Resumen de la Fase

La **Fase 6** del proyecto Accounting App se enfoca en la preparación para el despliegue serverless en AWS Lambda usando AWS SAM (Serverless Application Model). Esta fase está dividida en dos pasos:

### ✅ **Paso 1: Preparación de Artefactos para Despliegue** - COMPLETADO
- Configuración de AWS SAM
- Template.yaml para la aplicación
- Adaptación de Flask para Lambda
- Scripts de build y deploy
- Configuración de CI/CD
- Documentación completa

### 📋 **Paso 2: Generación de Componentes para Despliegue Productivo** - PENDIENTE
- Configuración de AWS RDS
- Configuración de API Gateway
- Configuración de monitoreo
- Optimización de costos

---

## 🎯 **Artefactos Generados**

### **1. Template AWS SAM (`template.yaml`)**
```yaml
# Configuración completa de la aplicación serverless
- API Gateway con CORS habilitado
- Lambda Function con Python 3.11
- CloudWatch Logs configurado
- IAM Roles y políticas
- Variables de entorno parametrizadas
```

### **2. Handler de Lambda (`application/lambda_handler.py`)**
```python
# Adaptador de Flask para AWS Lambda
- Manejo de eventos de API Gateway
- Conversión de requests/responses
- Logging para CloudWatch
- Manejo de errores robusto
```

### **3. Scripts de Automatización**
- **`scripts/build.py`**: Script de build automatizado
- **`scripts/build.sh`**: Script de build en bash
- **`package/deploy.sh`**: Script de despliegue
- **`.github/workflows/deploy.yml`**: CI/CD con GitHub Actions

### **4. Configuración de Entorno**
- **`package/lambda_config.py`**: Configuración específica para Lambda
- **`package/lambda_init.py`**: Script de inicialización
- **`package/env.json`**: Variables de entorno para testing
- **`package/.env.example`**: Template de variables de entorno

### **5. Documentación**
- **`package/DEPLOYMENT.md`**: Guía completa de despliegue
- **`README_FASE6.md`**: Este archivo con instrucciones detalladas

---

## 🛠️ **Cómo Usar los Artefactos**

### **1. Build Local**
```bash
# Ejecutar script de build
python scripts/build.py

# Verificar archivos generados
ls package/
```

### **2. Testing Local (Requiere AWS SAM CLI)**
```bash
# Instalar AWS SAM CLI
# https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html

# Ejecutar localmente
cd package
sam local start-api

# Testing de endpoints
curl http://localhost:3000/health
curl http://localhost:3000/tasks
```

### **3. Despliegue a AWS (Paso 2)**
```bash
# Configurar AWS CLI
aws configure

# Ejecutar build
python scripts/build.py

# Desplegar
cd package
./deploy.sh production
```

---

## 📊 **Arquitectura Serverless**

### **Componentes AWS**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │───▶│  Lambda Function│───▶│   RDS MySQL     │
│                 │    │                 │    │                 │
│ • CORS enabled  │    │ • Flask App     │    │ • MySQL 8.0     │
│ • Rate limiting │    │ • Python 3.11   │    │ • Multi-AZ      │
│ • Auth (future) │    │ • 512MB Memory  │    │ • Automated     │
└─────────────────┘    └─────────────────┘    │   Backups       │
                                              └─────────────────┘
```

### **Flujo de Request**
1. **API Gateway** recibe request HTTP
2. **Lambda** procesa con Flask
3. **RDS** almacena/recupera datos
4. **CloudWatch** registra logs y métricas

---

## 💰 **Costos Estimados**

| Servicio | Configuración | Costo Mensual |
|----------|---------------|----------------|
| **Lambda** | 1M requests, 400K GB-segundos | $6.87 |
| **API Gateway** | 1M requests | $3.50 |
| **RDS MySQL** | db.t3.micro | $15.00 |
| **CloudWatch** | Logs y métricas | $2.00 |
| **Total** | | **$27.37** |

---

## 🔧 **Configuración Detallada**

### **Variables de Entorno Requeridas**
```bash
# Base de Datos
DATABASE_HOST=your-rds-endpoint.region.rds.amazonaws.com
DATABASE_PORT=3306
DATABASE_NAME=accounting
DATABASE_USER=admin
DATABASE_PASSWORD=your-secure-password

# Aplicación
ENVIRONMENT=production
LOG_LEVEL=INFO

# AWS
AWS_REGION=us-east-1
```

### **Security Groups**
```bash
# RDS Security Group
- Inbound: MySQL (3306) from Lambda SG
- Outbound: All traffic

# Lambda Security Group  
- Inbound: None
- Outbound: All traffic to RDS
```

---

## 🚀 **Próximos Pasos (Paso 2)**

### **1. Configurar AWS RDS**
```bash
# Crear instancia RDS MySQL
aws rds create-db-instance \
    --db-instance-identifier accounting-app-db \
    --db-instance-class db.t3.micro \
    --engine mysql \
    --master-username admin \
    --master-user-password your-secure-password \
    --allocated-storage 20
```

### **2. Configurar Secrets Manager**
```bash
# Crear secret para contraseña
aws secretsmanager create-secret \
    --name "accounting-app/database-password" \
    --secret-string "your-secure-password"
```

### **3. Desplegar Aplicación**
```bash
# Build y deploy
python scripts/build.py
cd package
./deploy.sh production
```

### **4. Configurar Monitoreo**
```bash
# Crear alarmas CloudWatch
aws cloudwatch put-metric-alarm \
    --alarm-name "accounting-app-error-rate" \
    --metric-name Errors \
    --namespace AWS/Lambda \
    --statistic Sum \
    --period 300 \
    --threshold 5 \
    --comparison-operator GreaterThanThreshold
```

---

## 🧪 **Testing y Validación**

### **Health Check**
```bash
curl https://your-api-gateway-url.amazonaws.com/health
# Response: {"status": "ok", "service": "accounting-app"}
```

### **Testing de Endpoints**
```bash
# Crear tarea
curl -X POST https://your-api-gateway-url.amazonaws.com/tasks \
    -H "Content-Type: application/json" \
    -d '{"title": "Test Task", "description": "Test", "user_id": 1}'

# Listar tareas
curl https://your-api-gateway-url.amazonaws.com/tasks

# Completar tarea
curl -X POST https://your-api-gateway-url.amazonaws.com/tasks/1/complete
```

### **Testing de Performance**
```bash
# Instalar Apache Bench
sudo apt-get install apache2-utils

# Testing de carga
ab -n 1000 -c 10 https://your-api-gateway-url.amazonaws.com/health
```

---

## 📈 **Monitoreo y Alertas**

### **CloudWatch Logs**
```bash
# Ver logs de Lambda
aws logs filter-log-events \
    --log-group-name "/aws/lambda/accounting-app-function" \
    --start-time $(date -d '1 hour ago' +%s)000
```

### **Métricas Importantes**
- **Error Rate**: < 5%
- **Latencia**: < 5 segundos
- **Memory Usage**: < 80%
- **Cold Start Duration**: < 2 segundos

### **Alertas Recomendadas**
```bash
# Error rate > 5%
# Latencia > 5 segundos  
# Memory usage > 80%
# Costos > $30/mes
```

---

## 🔒 **Seguridad**

### **IAM Roles**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream", 
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

### **VPC Configuration**
- **Subnets**: Privadas para Lambda
- **Security Groups**: Restrictivos
- **NAT Gateway**: Para acceso a internet
- **VPC Endpoints**: Para servicios AWS

---

## 🛠️ **Troubleshooting**

### **Problemas Comunes**

#### **1. Cold Starts**
```bash
# Soluciones:
- Optimizar dependencias
- Usar Lambda Layers
- Configurar Provisioned Concurrency
- Reducir tamaño del package
```

#### **2. Errores de Conexión a BD**
```bash
# Verificar:
- Security Groups
- Credenciales
- Configuración de red
- VPC settings
```

#### **3. Timeouts**
```bash
# Ajustar:
- Lambda timeout (actual: 30s)
- API Gateway timeout
- RDS connection pool
```

---

## 📚 **Recursos Adicionales**

### **Documentación AWS**
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [Lambda Python Runtime](https://docs.aws.amazon.com/lambda/latest/dg/python-programming-model.html)
- [API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/)

### **Herramientas Útiles**
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
- [CloudWatch Logs Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html)

---

## 🎉 **Estado Actual**

### **✅ Completado**
- [x] Template AWS SAM
- [x] Handler de Lambda
- [x] Scripts de build y deploy
- [x] Configuración de CI/CD
- [x] Documentación completa
- [x] Variables de entorno
- [x] Testing local

### **📋 Pendiente (Paso 2)**
- [ ] Configuración de RDS
- [ ] Despliegue a AWS
- [ ] Configuración de monitoreo
- [ ] Optimización de costos
- [ ] Testing de producción

### **📊 Métricas**
- **Artefactos generados**: 15 archivos
- **Scripts de automatización**: 4 scripts
- **Documentación**: 2 archivos MD
- **Configuración**: Completa para despliegue

---

## 🚀 **Conclusión**

La **Fase 6 - Paso 1** está **completamente terminada** con todos los artefactos necesarios para el despliegue serverless. El proyecto está listo para la **Fase 6 - Paso 2** que incluye el despliegue real a AWS.

**Próximo paso**: Seguir las instrucciones detalladas en el plan de trabajo para configurar AWS RDS y hacer el despliegue productivo. 