# 🪙 Accounting App Backend

Backend para una aplicación de contabilidad, desarrollado en Python con Flask y siguiendo los principios de **Clean Architecture**.

Este proyecto está diseñado para ser escalable, mantenible y fácil de probar, separando las responsabilidades en capas claras: Dominio, Aplicación e Infraestructura.

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

### 5. Ejecutar Validaciones de Calidad

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

## 📚 Documentación Completa

Para una comprensión más profunda del proyecto, consulta la documentación detallada en los siguientes enlaces:

-   **[Arquitectura del Sistema](./docs/architecture/overview.md)**: Detalles sobre Clean Architecture y las capas del sistema.
-   **[Stack Tecnológico](./docs/tech-stack/components.md)**: Herramientas y versiones utilizadas.
-   **[Configuración del Entorno](./docs/setup/environment.md)**: Guías para configurar el proyecto.
-   **[Calidad del Código](./docs/quality/linting.md)**: Políticas de calidad y cómo ejecutar pruebas.
-   **[Base de Datos](./docs/database/migrations.md)**: Información sobre la estructura y migraciones.
-   **[Despliegue](./docs/deployment/process.md)**: Proceso de despliegue e infraestructura.
-   **[Flujo de Git](./docs/git/workflow.md)**: Describe el modelo de ramificación utilizado.

Para obtener pautas detalladas sobre cómo contribuir, consulta el archivo [CONTRIBUTING.md](./CONTRIBUTING.md).

---

