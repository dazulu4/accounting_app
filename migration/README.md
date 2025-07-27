# Migraciones de Base de Datos - Edición Empresarial

Gestión profesional de migraciones de bases de datos con Alembic, con características empresariales y soporte para múltiples entornos.

## Características Principales

-   **Configuración sensible al entorno** con detección automática de la URL de la base de datos.
-   **Nomenclatura profesional para migraciones** con marcas de tiempo y mensajes descriptivos.
-   **Soporte para múltiples entornos** (desarrollo, producción).
-   **Creación automática de backups** antes de las migraciones en entornos no productivos.
-   **Logging completo** con salida estructurada.
-   **Herramientas de validación** y verificación de migraciones.
-   **Optimización para MySQL** con índices y restricciones adecuadas.
-   **Validación de datos** con restricciones de integridad.
-   **Sistema de manejo de errores** integrado con el sistema centralizado.

## Guía de Inicio Rápido

### 1. Configuración del Entorno

Asegúrate de que tus variables de entorno estén configuradas en el archivo `.env`. Puedes copiar `env.example` como punto de partida.

### 2. Comandos Básicos de Migración

```bash
# Aplicar todas las migraciones pendientes
./scripts/migrate.sh upgrade

# Revisar el estado actual de la migración
./scripts/migrate.sh current

# Ver el historial de migraciones
./scripts/migrate.sh history
```

### 3. Creación de Nuevas Migraciones

```bash
# Generar una migración con "autogenerate" (recomendado)
poetry run alembic revision --autogenerate -m "describir_el_cambio"

# Crear una plantilla de migración vacía
poetry run alembic revision -m "describir_migracion_de_datos"
```

## Scripts de Migración

### `scripts/migrate.sh`

Script profesional para la ejecución de migraciones. Es la forma recomendada de ejecutar las migraciones, ya que asegura que se cargue el entorno correcto.

---

-   **`new`** - Crea un nuevo archivo de migración con autogenerate.
    -   **Script:** `./scripts/migrate.sh new "mi_mensaje_de_migracion"`
    -   **Comando base:** `poetry run alembic revision --autogenerate -m "mi_mensaje_de_migracion"`

-   **`upgrade`** - Aplica las migraciones pendientes.
    -   **Script:** `./scripts/migrate.sh upgrade`
    -   **Comando base:** `poetry run alembic upgrade head`

-   **`downgrade`** - Revierte la última migración.
    -   **Script:** `./scripts/migrate.sh downgrade`
    -   **Comando base:** `poetry run alembic downgrade -1`

-   **`current`** - Muestra la versión actual de la migración.
    -   **Script:** `./scripts/migrate.sh current`
    -   **Comando base:** `poetry run alembic current`

-   **`history`** - Muestra el historial de migraciones.
    -   **Script:** `./scripts/migrate.sh history`
    -   **Comando base:** `poetry run alembic history`

**Uso:**
```bash
# Ejemplo: Crear una nueva migración
./scripts/migrate.sh new "añadir_columna_email_a_usuarios"

# Ejemplo: Aplicar migraciones
./scripts/migrate.sh upgrade
```

## Archivos de Configuración

### `alembic.ini`

Configuración de Alembic de nivel empresarial con:
-   Nomenclatura profesional para archivos de migración con timestamps.
-   Configuración del motor específica para MySQL.
-   Ajustes específicos por entorno.
-   Configuración de logging completa.

### `migration/env.py`

Configuración de migración sensible al entorno con:
-   Detección automática de la URL de la base de datos desde variables de entorno.
-   Conexión a la base de datos de nivel empresarial con pooling.
-   Integración de logging estructurado.
-   Soporte para múltiples entornos.
-   Manejo adecuado de errores.

## Estructura de Archivos de Migración

Las migraciones siguen convenciones de nomenclatura empresariales:
```
YYYYMMDD_HHMM_revision_message.py
```
Ejemplo: `20250119_1430_ba4800daf143_create_tasks_table.py`

## Esquema de la Base de Datos

### Tabla `tasks`

La tabla principal `tasks` con un diseño de esquema de nivel empresarial:

```sql
CREATE TABLE tasks (
    task_id CHAR(36) NOT NULL COMMENT 'Identificador único de la tarea (UUID)',
    title VARCHAR(200) NOT NULL COMMENT 'Título o resumen de la tarea (no puede estar vacío)',
    description TEXT NOT NULL COMMENT 'Descripción detallada de la tarea (no puede estar vacío)',
    user_id INTEGER NOT NULL COMMENT 'ID del usuario propietario de la tarea',
    status VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT 'Estado de la tarea (pending, in_progress, completed, cancelled)',
    priority VARCHAR(10) NOT NULL DEFAULT 'medium' COMMENT 'Prioridad de la tarea (low, medium, high, urgent)',
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    completed_at DATETIME(6) NULL COMMENT 'Timestamp de finalización de la tarea',
    
    PRIMARY KEY (task_id),
    INDEX idx_tasks_user_id (user_id),
    INDEX idx_tasks_status (status),
    INDEX idx_tasks_user_status (user_id, status),
    INDEX idx_tasks_priority (priority),
    INDEX idx_tasks_created_at (created_at),
    INDEX idx_tasks_completed (status, completed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## Configuración Específica por Entorno

### Desarrollo (Development)
-   Base de datos MySQL local.
-   Logging de migraciones habilitado.
-   Sin backups automáticos.
-   Validación relajada.

### Producción (Production)
-   Base de datos de Producción con alta disponibilidad (High Availability).
-   Backups obligatorios antes de cualquier migración.
-   Confirmación extra para operaciones destructivas.
-   Logging de auditoría completo.
-   Procedimientos de rollback documentados.

## Buenas Prácticas

### Creación de Migraciones
1.  **Usa nombres descriptivos** en formato `snake_case`.
2.  **Prueba las migraciones** en desarrollo primero.
3.  **Revisa las migraciones generadas** antes de aplicarlas.
4.  **Incluye procedimientos de rollback** para migraciones complejas.
5.  **Documenta las migraciones de datos** con comentarios.

### Ejecución de Migraciones
1.  **Siempre haz un backup** antes de las migraciones a producción.
2.  **Monitorea el rendimiento** durante migraciones grandes.
3.  **Ten un plan de rollback** listo.
4.  **Coordina con el equipo** para los despliegues a producción.

### Convenciones de Nomenclatura
-   **Crear tablas**: `create_[table_name]_table`
-   **Añadir columnas**: `add_[column_name]_to_[table_name]`
-   **Eliminar columnas**: `remove_[column_name]_from_[table_name]`
-   **Añadir índices**: `add_index_[table_name]_[column_name]`
-   **Migraciones de datos**: `migrate_[description]_data`

## Solución de Problemas (Troubleshooting)

### Problemas Comunes

**La migración falla con un error de conexión:**
```bash
# 1. Asegúrate de que tu archivo .env tiene las credenciales correctas.
# 2. Revisa la conectividad de la base de datos:
mysql -h $DB_HOST -u $DB_USERNAME -p$DB_PASSWORD $DB_NAME
```

**`autogenerate` no detecta los cambios:**
```bash
# Verificar que los modelos se importen correctamente en la capa de infraestructura
python -c "from infrastructure.helpers.database.connection import Base; print(Base.metadata.tables.keys())"
```

**Conflictos de migración:**
```bash
# Revisar el estado actual
./scripts/migrate.sh current

# Ver el historial de migraciones
./scripts/migrate.sh history
```

### Procedimientos de Recuperación

**Revertir la última migración:**
```bash
./scripts/migrate.sh downgrade
```

**Restaurar desde un backup:**
```bash
# Esta operación es manual y depende de tu estrategia de backups.
# Ejemplo para producción (requiere asistencia de un DBA):
mysql -h $DB_HOST -u $DB_USERNAME -p$DB_PASSWORD $DB_NAME < backup_file.sql
```

## Monitoreo y Mantenimiento

-   **Verificación regular de backups** para entornos de producción.
-   **Monitoreo del rendimiento de migraciones** para tablas grandes.
-   **Análisis del uso de índices** después de cambios en el esquema.
-   **Monitoreo del tamaño de la base de datos** después de las migraciones.
-   **Limpieza regular** de archivos de backup antiguos.

## Soporte

Para problemas o preguntas sobre migraciones:
1.  Revisa esta documentación.
2.  Revisa los logs de migración.
3.  Valida la configuración del entorno.
4.  Prueba primero en el entorno de desarrollo.
5.  Contacta al equipo de base de datos para problemas en producción.
