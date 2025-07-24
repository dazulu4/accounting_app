# Ejecución de la Aplicación en Local

Este documento detalla los pasos para ejecutar la aplicación en tu entorno de desarrollo local, una vez que hayas completado la [configuración del entorno](./environment.md).

---

## 1. Aplicar las Migraciones de la Base de Datos

Antes de iniciar la aplicación por primera vez, es crucial preparar la base de datos. Las migraciones se encargan de crear todas las tablas y relaciones necesarias.

Con el contenedor de Docker de la base de datos ya corriendo, ejecuta el siguiente comando desde la raíz del proyecto:

```bash
poetry run alembic upgrade head
```

-   `poetry run`: Ejecuta el comando dentro del entorno virtual del proyecto.
-   `alembic upgrade head`: Aplica todas las migraciones pendientes hasta la más reciente.

Si todo va bien, verás logs de Alembic indicando que las migraciones se han ejecutado.

---

## 2. Iniciar el Servidor de Desarrollo

Con la base de datos lista, ya puedes iniciar el servidor de Flask.

Ejecuta el siguiente comando desde la raíz del proyecto:

```bash
poetry run python application/main.py
```

Si el inicio es exitoso, verás un mensaje en la consola similar a este:

```
 * Running on http://127.0.0.1:8000
 * Press CTRL+C to quit
```

Esto significa que la aplicación está corriendo y escuchando peticiones en el puerto `8000`.

---

## 3. Verificar que la Aplicación Esté Funcionando

Puedes hacer una simple verificación para asegurarte de que todo funciona correctamente. Por ejemplo, puedes usar `curl` o un cliente de API como Postman para hacer una petición a uno of the endpoints.

### Ejemplo con `curl`

Abre una nueva terminal y ejecuta:

```bash
curl http://127.0.0.1:8000/api/users
```

Si la aplicación funciona, deberías recibir una respuesta JSON con una lista de usuarios (o una lista vacía si aún no hay datos).

```json
[
  {
    "id": 1,
    "name": "Admin User",
    "email": "admin@example.com",
    "status": "ACTIVE"
  }
]
```

Si recibes una respuesta como esta, ¡felicidades! Tu entorno de desarrollo está configurado y funcionando correctamente. 