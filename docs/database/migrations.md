# Gestión de Migraciones con Alembic

A medida que una aplicación evoluciona, el esquema de la base de datos (tablas, columnas, etc.) necesita cambiar. Gestionar estos cambios de forma manual es propenso a errores y difícil de coordinar en un equipo. Por eso, utilizamos **Alembic**, una herramienta de migración de bases de datos para SQLAlchemy.

---

## ¿Qué es Alembic?

Alembic trata los cambios en el esquema de la base de datos como **versiones**, de la misma manera que Git trata los cambios en el código. Cada cambio se guarda en un *script de migración*, que contiene el código Python necesario para aplicar (y revertir) dicho cambio.

**Ventajas de usar Alembic**:
-   **Control de Versiones**: Cada estado del esquema de la DB tiene un identificador único.
-   **Reproducibilidad**: Cualquier desarrollador puede recrear el esquema de la base de datos en cualquier versión.
-   **Trabajo en Equipo**: Facilita la coordinación de cambios en la base de datos entre varios desarrolladores.

---

## Comandos Principales de Alembic

Todos los comandos de Alembic deben ejecutarse con `poetry run` para que se ejecuten en el entorno virtual correcto.

### Ver la Versión Actual

Para ver en qué versión se encuentra actualmente tu base de datos, puedes ejecutar:

```bash
poetry run alembic current
```

### Crear una Nueva Migración

Cuando haces un cambio en los modelos de SQLAlchemy (por ejemplo, añades una nueva columna a una tabla), necesitas generar un nuevo script de migración.

Alembic puede detectar automáticamente muchos de estos cambios y generar el script por ti:

```bash
poetry run alembic revision --autogenerate -m "Descripción del cambio"
```
-   `--autogenerate`: Le pide a Alembic que compare los modelos de SQLAlchemy con el estado actual de la base de datos y genere las diferencias.
-   `-m "..."`: Un mensaje descriptivo para el script de migración.

Esto creará un nuevo archivo en `migration/versions/` con los cambios detectados. **Siempre debes revisar el archivo generado** para asegurarte de que es correcto antes de aplicarlo.

### Aplicar Migraciones (Upgrade)

Para aplicar todas las migraciones pendientes y llevar la base de datos a la última versión, ejecuta:

```bash
poetry run alembic upgrade head
```
`head` es una referencia a la última versión disponible.

### Revertir Migraciones (Downgrade)

Para revertir la última migración aplicada, puedes ejecutar:

```bash
poetry run alembic downgrade -1
```

---

## Ubicación de los Archivos de Migración

-   **Configuración de Alembic**: `alembic.ini` en la raíz del proyecto.
-   **Entorno de Migración**: `migration/env.py`, donde se configura la conexión a la base de datos.
-   **Scripts de Migración**: `migration/versions/`, donde se guardan todos los scripts de migración generados.

---

Para entender qué tablas y relaciones se gestionan con estas migraciones, consulta la [Estructura General de la Base de Datos](./structure.md). 