# Estructura de la Base de Datos

Este documento ofrece una visión general de la estructura de la base de datos `accounting`. El objetivo es entender la entidad principal y cómo se relaciona con datos externos.

El esquema de la base de datos es gestionado a través de las migraciones de Alembic, y los modelos de SQLAlchemy son la fuente de verdad para la estructura de la tabla.

---

## Tabla Principal: `tasks`

La base de datos se centra en una única entidad de negocio principal: las **Tareas** (`tasks`).

-   **Propósito**: Almacena las tareas contables que deben realizarse.
-   **Campos Clave**:
    -   `task_id`: Identificador único de la tarea (UUID en formato CHAR(36)).
    -   `title`: Título de la tarea (VARCHAR(200), no puede estar vacío).
    -   `description`: Descripción detallada de la tarea (TEXT, no puede estar vacío).
    -   `user_id`: ID del usuario propietario de la tarea (INTEGER). Este ID corresponde a un usuario definido fuera de la base de datos (en un archivo JSON).
    -   `status`: Estado de la tarea (VARCHAR(20), e.g., `pending`, `in_progress`, `completed`, `cancelled`).
    -   `priority`: Prioridad de la tarea (VARCHAR(10), e.g., `low`, `medium`, `high`, `urgent`).
    -   `created_at`: Fecha y hora de creación (DATETIME).
    -   `updated_at`: Fecha y hora de la última actualización (DATETIME).
    -   `completed_at`: Fecha y hora de finalización (DATETIME, puede ser nulo).

### Estados de Tarea

El sistema maneja los siguientes estados de tarea con transiciones controladas:

- **PENDING**: Tarea creada pero no iniciada
- **IN_PROGRESS**: Tarea en progreso activo
- **COMPLETED**: Tarea finalizada exitosamente
- **CANCELLED**: Tarea cancelada (estado terminal)

### Prioridades de Tarea

- **LOW**: Prioridad baja
- **MEDIUM**: Prioridad media (por defecto)
- **HIGH**: Prioridad alta
- **URGENT**: Prioridad urgente

---

## Relación con Datos Externos (Usuarios)

Aunque la base de datos solo contiene la tabla `tasks`, existe una relación conceptual importante:

-   **Cada Tarea pertenece a un Usuario**:
    -   La tabla `tasks` tiene una columna `user_id`. Este campo no es una clave foránea a otra tabla de la base de datos, sino un identificador que vincula la tarea con un usuario específico.
    -   La información de los usuarios (a la que apunta `user_id`) se gestiona a través del `FakeUserService`, un repositorio en memoria para desarrollo y testing.

---

## Consideraciones Adicionales

-   **Clave Primaria**: La tabla `tasks` tiene una clave primaria (`PRIMARY KEY`) para identificar de forma única cada registro.
-   **Índices**: Se utilizan índices en columnas que se usan frecuentemente en búsquedas (como `user_id` y `status`) para mejorar el rendimiento de las consultas.
-   **Evolución del Esquema**: Cualquier cambio en esta estructura debe realizarse a través de un nuevo script de migración de Alembic para asegurar la consistencia en todos los entornos. 