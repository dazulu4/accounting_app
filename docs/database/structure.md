# Estructura General de la Base de Datos

Este documento ofrece una visión general de la estructura de la base de datos `accounting`, sin entrar en el detalle de cada columna. El objetivo es entender las entidades principales y cómo se relacionan entre sí.

El esquema de la base de datos es gestionado a través de las migraciones de Alembic, y los modelos de SQLAlchemy son la fuente de verdad para la estructura de las tablas.

---

## Tablas Principales

La base de datos se centra en dos entidades de negocio principales: **Usuarios** y **Tareas**.

### 1. Tabla `users`

-   **Propósito**: Almacena la información de los usuarios del sistema.
-   **Campos Clave**:
    -   `id`: Identificador único del usuario.
    -   `name`: Nombre del usuario.
    -   `email`: Correo electrónico (debe ser único).
    -   `status`: Estado del usuario (e.g., `ACTIVE`, `INACTIVE`).

### 2. Tabla `tasks`

-   **Propósito**: Almacena las tareas contables que deben realizarse.
-   **Campos Clave**:
    -   `id`: Identificador único de la tarea (UUID).
    -   `title`: Título de la tarea.
    -   `description`: Descripción detallada de la tarea.
    -   `status`: Estado de la tarea (e.g., `NEW`, `COMPLETED`).
    -   `created_at`: Fecha y hora de creación.
    -   `completed_at`: Fecha y hora de finalización.
    -   `user_id`: Clave foránea que referencia al usuario asignado.

---

## Relaciones entre Tablas

La principal relación en la base de datos es entre `users` y `tasks`:

-   **Un Usuario puede tener muchas Tareas**:
    -   La tabla `tasks` tiene una columna `user_id` que es una clave foránea (`FOREIGN KEY`) que apunta al `id` de la tabla `users`.
    -   Esto establece una relación de **uno a muchos** (one-to-many): un usuario puede estar asociado a múltiples tareas, pero cada tarea pertenece a un único usuario.

---

## Consideraciones Adicionales

-   **Claves Primarias**: Todas las tablas tienen una clave primaria (`PRIMARY KEY`) para identificar de forma única cada registro.
-   **Índices**: Se utilizan índices en las claves foráneas y en otras columnas que se usan frecuentemente en búsquedas para mejorar el rendimiento de las consultas.
-   **Evolución del Esquema**: Cualquier cambio en esta estructura debe realizarse a través de un nuevo script de migración de Alembic para asegurar la consistencia en todos los entornos. 