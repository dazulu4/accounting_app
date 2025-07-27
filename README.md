# 📋 Task Manager Contable

Backend para un **Task Manager especializado en tareas contables**, desarrollado en Python con Flask y siguiendo los principios de **Clean Architecture**.

Este sistema permite a los equipos de contabilidad gestionar, organizar y dar seguimiento a sus tareas diarias de manera eficiente, desde conciliaciones bancarias hasta cierre de períodos fiscales.

## 🚀 Características Principales

- ✅ **Gestión de tareas contables**: Crear, asignar y dar seguimiento a tareas específicas
- 👥 **Colaboración de equipo**: Asignar tareas a diferentes miembros del equipo contable
- 📊 **Estados de seguimiento**: Pending, In Progress, Completed, Cancelled
- 🔄 **Priorización**: Gestión de prioridades (Low, Medium, High, Urgent)
- 📈 **Organización por usuario**: Visualizar tareas asignadas a cada contador
- 🛡️ **Manejo robusto de errores**: Sistema centralizado de errores con códigos HTTP apropiados
- 📝 **Validación de datos**: Validación automática con Pydantic
- 🔍 **Logging estructurado**: Logs detallados para monitoreo y debugging

---

## 🎯 ¿Qué es Task Manager Contable?

**Task Manager Contable** es una herramienta de gestión de tareas específicamente diseñada para departamentos de contabilidad. No es un sistema contable completo, sino un organizador de las actividades contables que facilita:

- ✅ **Gestión de tareas contables**: Crear, asignar y dar seguimiento a tareas específicas
- 👥 **Colaboración de equipo**: Asignar tareas a diferentes miembros del equipo contable
- 📊 **Estados de seguimiento**: Pending, In Progress, Completed, Cancelled
- 🔄 **Priorización**: Gestión de prioridades (Low, Medium, High, Urgent)
- 📈 **Organización por usuario**: Visualizar tareas asignadas a cada contador

### Casos de Uso Típicos
- Preparación de estados financieros
- Conciliaciones bancarias
- Procesamiento de facturas
- Cierre mensual/anual
- Auditorías internas
- Tareas de cumplimiento fiscal

### Arquitectura del Sistema

El proyecto sigue **Clean Architecture** con estas capas:

- **🌟 Domain**: Entidades de negocio (Task, User) y reglas de negocio
- **⚙️ Application**: Casos de uso (CreateTask, CompleteTask, ListTasks)
- **🔌 Infrastructure**: Adaptadores externos (HTTP routes, Database, etc.)

### Manejo de Errores

El sistema implementa un **manejo centralizado de errores** con códigos HTTP apropiados:

- **400**: Errores de validación de datos de entrada
- **404**: Recursos no encontrados
- **422**: Errores de reglas de negocio
- **500**: Errores técnicos del sistema
- **429**: Rate limiting (más de 10 peticiones por minuto)

---

## 🚀 Guía de Inicio Rápido

Sigue estos pasos para tener el entorno de desarrollo funcionando en tu máquina local.

### 1. Requisitos Previos

- **Python**: `3.11` o superior.
- **Poetry**: Gestor de dependencias. [Instrucciones de instalación](https://python-poetry.org/docs/#installation).
- **Git**: Sistema de control de versiones.
- **MySQL**: Una instancia de base de datos MySQL accesible. Se proporciona una configuración con Docker para un inicio rápido (opcional).

### 2. Configuración del Entorno

```bash
# 1. Clona el repositorio
git clone <URL_DEL_REPOSITORIO>
cd accounting_app

# 2. Instala las dependencias del proyecto
poetry install

# 3. (Opcional) Levanta la base de datos con Docker
docker-compose -f local/docker/docker-compose.yml up -d

# 4. Copia el archivo de ejemplo para las variables de entorno
cp env.example .env
```

> ⚠️ **Nota**: El archivo `.env` ya viene pre-configurado para conectarse a una base de datos local estándar (incluida la de Docker). Si tu configuración de MySQL es diferente, ajusta las variables en este archivo.

### 3. Aplicar Migraciones de la Base de Datos

Una vez que la base de datos esté corriendo y configurada en tu archivo `.env`, necesitas aplicar las migraciones para crear las tablas necesarias.

```bash
poetry run alembic upgrade head
```

### 4. Ejecutar la Aplicación

Con el entorno configurado y la base de datos lista, puedes iniciar el servidor:

```bash
poetry run python application/main.py
```

El servidor estará disponible en `http://127.0.0.1:8000`.

### 5. Endpoints Principales

Una vez que el servidor esté corriendo, puedes interactuar con estos endpoints principales:

```bash
# Health check y versión
GET /api/health
GET /api/version

# Gestión de tareas
POST /api/tasks
{
  "title": "Conciliación bancaria enero",
  "description": "Conciliar cuenta corriente principal",
  "user_id": 1,
  "priority": "high"
}

PUT /api/tasks/{task_id}/complete

# Gestión de usuarios
GET /api/users
GET /api/users/{user_id}/tasks
```

### 6. Ejemplos de Respuestas

**Crear tarea exitosa (201):**
```json
{
  "task_id": "3b403685-66a9-4697-9876-47fe8e06dbbb",
  "title": "Conciliación bancaria enero",
  "description": "Conciliar cuenta corriente principal",
  "user_id": 1,
  "status": "pending",
  "priority": "high",
  "created_at": "2025-01-27T13:52:54.418313+00:00"
}
```

**Error de validación (400):**
```json
{
  "error": {
    "type": "VALIDATION_ERROR",
    "code": "VALIDATION_ERROR",
    "message": "Validation failed for the following fields: title",
    "timestamp": "2025-01-27T13:52:54.418313+00:00",
    "request_id": "1e531181-0961-4825-b251-a524df256614",
    "path": "/api/tasks",
    "method": "POST",
    "details": {
      "field_errors": {
        "title": "Task title cannot be empty or whitespace"
      }
    }
  }
}
```

### 7. Ejecutar Validaciones de Calidad

Para asegurar la calidad del código, puedes ejecutar las siguientes herramientas:

```bash
# Ejecutar pruebas unitarias y de integración
poetry run pytest

# Analizar cobertura de las pruebas
poetry run pytest --cov

# Revisar formateo, linting y tipos estáticos
poetry run black . --check
poetry run isort . --check-only
poetry run flake8
poetry run mypy .

# Ejecutar todas las validaciones de calidad
./scripts/quality.sh
```

---

## 🏗️ Arquitectura del Sistema

El proyecto sigue **Clean Architecture** con estas capas:

- **🌟 Domain**: Entidades de negocio (Task, User) y reglas de negocio
- **⚙️ Application**: Casos de uso (CreateTask, CompleteTask, ListTasks)
- **🔌 Infrastructure**: Adaptadores externos (HTTP routes, Database, etc.)

### Estructura del Proyecto
```
accounting_app/
├── domain/           # Capa de dominio (entidades, use cases, excepciones)
│   ├── entities/     # Entidades de negocio (TaskEntity, UserEntity)
│   ├── usecases/     # Casos de uso (CreateTaskUseCase, CompleteTaskUseCase)
│   ├── exceptions/   # Excepciones de negocio y mapeo de errores
│   ├── gateways/     # Interfaces para repositorios
│   └── enums/        # Enumeraciones de dominio
├── application/      # Configuración y punto de entrada
│   ├── config/       # Configuración de la aplicación
│   ├── schemas/      # Esquemas de validación (Pydantic)
│   └── container.py  # Inyección de dependencias
├── infrastructure/   # Adaptadores y drivers externos
│   ├── entrypoints/  # Endpoints HTTP (Flask routes)
│   ├── driven_adapters/ # Repositorios y adaptadores
│   └── helpers/      # Utilidades (logging, errores, middleware)
├── tests/            # Pruebas unitarias y de integración
├── migration/        # Migraciones de base de datos (Alembic)
└── docs/             # Documentación del proyecto
```

---

## 📚 Documentación Completa

Para una comprensión más profunda del proyecto, consulta la documentación detallada en los siguientes enlaces:

-   **[Arquitectura del Sistema](./docs/architecture/overview.md)**: Detalles sobre Clean Architecture y las capas del sistema.
-   **[Stack Tecnológico](./docs/tech-stack/components.md)**: Herramientas y versiones utilizadas.
-   **[Configuración del Entorno](./docs/setup/environment.md)**: Guías para configurar el proyecto.
-   **[Calidad del Código](./docs/quality/linting.md)**: Políticas de calidad y cómo ejecutar pruebas.
-   **[Base de Datos](./docs/database/migrations.md)**: Información sobre la estructura y migraciones.
-   **[Despliegue](./docs/deployment/process.md)**: Proceso de despliegue e infraestructura.
-   **[Flujo de Git](./docs/git/workflow.md)**: Describe el modelo de ramificación utilizado.

---

## 🤝 Contribuciones

Este proyecto está diseñado para ser mantenible y extensible. Si deseas contribuir:

1. Lee nuestro [CONTRIBUTING.md](./CONTRIBUTING.md)
2. Crea un fork del proyecto
3. Desarrolla tu feature siguiendo Clean Architecture
4. Asegúrate de que todas las pruebas pasen
5. Envía un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](./LICENSE) para más detalles.

