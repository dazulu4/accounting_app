# Guía de Ejecución Local

Este documento te guía paso a paso para ejecutar el **Task Manager Contable** en tu entorno de desarrollo local.

---

## 1. Verificación de Prerrequisitos

Antes de ejecutar la aplicación, asegúrate de que tienes todo configurado correctamente:

### Verificar el Entorno
```bash
# Verificar que Poetry está instalado
poetry --version

# Verificar que las dependencias están instaladas
poetry show

# Verificar que el archivo .env existe
ls -la .env
```

### Verificar la Base de Datos
```bash
# Si usas Docker, verificar que el contenedor está corriendo
docker ps | grep mysql

# Si usas MySQL local, verificar que el servicio está activo
mysql -u root -p -e "SELECT 1;"
```

---

## 2. Aplicar Migraciones de Base de Datos

Antes de ejecutar la aplicación, necesitas aplicar las migraciones para crear las tablas necesarias:

```bash
# Aplicar todas las migraciones pendientes
poetry run alembic upgrade head

# Verificar el estado de las migraciones
poetry run alembic current
```

### Verificar las Tablas Creadas
```bash
# Conectar a la base de datos y verificar las tablas
mysql -u root -ppassword accounting -e "SHOW TABLES;"
```

---

## 3. Ejecutar la Aplicación

### Opción 1: Ejecución Directa (Recomendado para Desarrollo)

```bash
# Ejecutar la aplicación en modo desarrollo
poetry run python application/main.py
```

### Opción 2: Usando Flask CLI

```bash
# Configurar variables de entorno para Flask
export FLASK_APP=application/main.py
export FLASK_ENV=development

# Ejecutar con Flask
poetry run flask run --host=127.0.0.1 --port=8000
```

### Opción 3: Ejecución en Segundo Plano

```bash
# Ejecutar en segundo plano
nohup poetry run python application/main.py > app.log 2>&1 &

# Verificar que está corriendo
ps aux | grep python
```

---

## 4. Verificar que la Aplicación Funciona

Una vez que la aplicación esté corriendo, puedes verificar que funciona correctamente:

### Health Check
```bash
# Verificar el endpoint de salud
curl http://127.0.0.1:8000/api/health

# Respuesta esperada:
# {
#   "status": "healthy",
#   "timestamp": "2025-01-27T14:30:00.000Z",
#   "version": "0.1.0"
# }
```

### Verificar la Versión
```bash
# Verificar el endpoint de versión
curl http://127.0.0.1:8000/api/version

# Respuesta esperada:
# {
#   "version": "0.1.0",
#   "environment": "development"
# }
```

### Verificar los Logs
```bash
# Ver los logs de la aplicación
tail -f app.log

# O si ejecutas directamente, los logs aparecerán en la consola
```

---

## 5. Probar los Endpoints Principales

Una vez que la aplicación esté funcionando, puedes probar los endpoints principales:

### Crear una Tarea
```bash
curl -X POST http://127.0.0.1:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Conciliación bancaria enero",
    "description": "Conciliar cuenta corriente principal",
    "user_id": 1,
    "priority": "high"
  }'
```

### Listar Usuarios
```bash
curl http://127.0.0.1:8000/api/users
```

### Listar Tareas de un Usuario
```bash
curl http://127.0.0.1:8000/api/users/1/tasks
```

### Completar una Tarea
```bash
curl -X PUT http://127.0.0.1:8000/api/tasks/1/complete
```

---

## 6. Configuración de Desarrollo Avanzada

### Modo Debug
Para desarrollo con recarga automática y debugging:

```bash
# Habilitar modo debug
export APP_DEBUG=true

# Ejecutar con debugging
poetry run python -m debugpy --listen 5678 application/main.py
```

### Configuración de Logging
```bash
# Cambiar nivel de logging
export LOG_LEVEL=DEBUG

# Cambiar formato de logs
export LOG_FORMAT=text
```

### Configuración de CORS
```bash
# Permitir orígenes específicos
export CORS_ORIGINS="http://localhost:3000,http://127.0.0.1:3000,http://localhost:8080"
```

---

## 7. Monitoreo y Debugging

### Ver Logs en Tiempo Real
```bash
# Ver logs de la aplicación
tail -f app.log

# Ver logs con filtros
grep "ERROR" app.log
grep "WARNING" app.log
```

### Verificar Recursos del Sistema
```bash
# Verificar uso de memoria
ps aux | grep python

# Verificar puertos en uso
netstat -tulpn | grep 8000

# Verificar conexiones a la base de datos
mysql -u root -ppassword -e "SHOW PROCESSLIST;" accounting
```

### Debugging con Python Debugger
```bash
# Ejecutar con pdb habilitado
poetry run python -m pdb application/main.py

# O agregar breakpoints en el código
import pdb; pdb.set_trace()
```

---

## 8. Solución de Problemas Comunes

### Problema: Puerto 8000 ya está en uso
```bash
# Verificar qué proceso usa el puerto
lsof -i :8000

# Terminar el proceso
kill -9 <PID>

# O usar un puerto diferente
poetry run python application/main.py --port 8001
```

### Problema: Error de conexión a la base de datos
```bash
# Verificar que MySQL está corriendo
docker ps | grep mysql

# Verificar las variables de entorno
echo $DATABASE_HOST
echo $DATABASE_PORT

# Probar conexión manual
mysql -h $DATABASE_HOST -P $DATABASE_PORT -u $DATABASE_USERNAME -p$DATABASE_PASSWORD $DATABASE_NAME
```

### Problema: Error de migraciones
```bash
# Verificar el estado de las migraciones
poetry run alembic current

# Revertir y volver a aplicar
poetry run alembic downgrade -1
poetry run alembic upgrade head

# Verificar las tablas
mysql -u root -ppassword accounting -e "SHOW TABLES;"
```

### Problema: Dependencias faltantes
```bash
# Reinstalar dependencias
poetry install --sync

# Verificar que todas están instaladas
poetry show
```

---

## 9. Detener la Aplicación

### Si está ejecutándose en primer plano
```bash
# Presionar Ctrl+C en la terminal
```

### Si está ejecutándose en segundo plano
```bash
# Encontrar el proceso
ps aux | grep python

# Terminar el proceso
kill -9 <PID>

# O usar pkill
pkill -f "application/main.py"
```

---

## 10. Limpieza del Entorno

### Limpiar Logs
```bash
# Limpiar logs antiguos
rm -f app.log
rm -f *.log
```

### Limpiar Cache
```bash
# Limpiar cache de Python
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### Reiniciar Base de Datos (Solo Desarrollo)
```bash
# Detener y reiniciar MySQL
docker-compose -f local/docker/docker-compose.yml down
docker-compose -f local/docker/docker-compose.yml up -d

# Reaplicar migraciones
poetry run alembic upgrade head
```

---

Una vez que tengas la aplicación corriendo localmente, puedes comenzar a desarrollar nuevas funcionalidades. Para más información sobre el desarrollo, consulta la [Guía de Desarrollo](./../architecture/development-guide.md). 