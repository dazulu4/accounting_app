# 📋 Task Manager Contable

Backend para un **Task Manager especializado en tareas contables**, desarrollado en Python con Flask y siguiendo los principios de **Clean Architecture**.

Este sistema permite a los equipos de contabilidad gestionar, organizar y dar seguimiento a sus tareas diarias de manera eficiente, desde conciliaciones bancarias hasta cierre de períodos fiscales.

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
# Health check
GET /api/health

# Crear una nueva tarea
POST /api/tasks
{
  "title": "Conciliación bancaria enero",
  "description": "Conciliar cuenta corriente principal",
  "user_id": 1,
  "priority": "high"
}

# Completar una tarea
PUT /api/tasks/{task_id}/complete

# Listar tareas por usuario
GET /api/users/{user_id}/tasks

# Listar todos los usuarios
GET /api/users
```

### 6. Ejecutar Validaciones de Calidad

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
├── domain/           # Capa de dominio (entidades, use cases)
├── application/      # Configuración y punto de entrada
├── infrastructure/   # Adaptadores y drivers externos
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

