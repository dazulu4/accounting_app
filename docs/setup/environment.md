# Configuración del Entorno de Desarrollo

Este documento describe en detalle los requisitos y la configuración necesaria para levantar el entorno de desarrollo local.

---

## 1. Requisitos de Software

Asegúrate de tener instaladas las siguientes herramientas en tu sistema:

-   **Python**: Se requiere una versión `>=3.11` y `<3.14`. Puedes verificar tu versión con `python --version`.
-   **Poetry**: Es el gestor de dependencias del proyecto. Si no lo tienes, sigue las [instrucciones oficiales de instalación](https://python-poetry.org/docs/#installation).
-   **Git**: El sistema de control de versiones.
-   **Docker y Docker Compose**: Necesarios para levantar la base de datos MySQL de forma aislada.

---

## 2. Instalación de Dependencias

Una vez que hayas clonado el repositorio, el siguiente paso es instalar todas las dependencias de Python que el proyecto necesita. `Poetry` se encarga de esto de manera muy sencilla.

Desde la raíz del proyecto, ejecuta:

```bash
poetry install
```

Este comando hará dos cosas:
1.  Creará un **entorno virtual** específico para este proyecto, para aislar sus dependencias.
2.  Instalará todas las librerías listadas en el archivo `pyproject.toml` (y fijadas en `poetry.lock`).

---

## 3. Variables de Entorno

La aplicación se configura mediante variables de entorno, siguiendo las mejores prácticas de [The Twelve-Factor App](https://12factor.net/config).

### Archivo `.env`

Para el desarrollo local, estas variables se gestionan a través de un archivo `.env` en la raíz del proyecto.

1.  **Copia el archivo de ejemplo**:
    ```bash
    cp env.example .env
    ```

2.  **Contenido del `.env`**:
    El archivo `.env` ya viene pre-configurado con los valores necesarios para conectarse a la base de datos que se levanta con Docker. No deberías necesitar cambiar nada para que la aplicación funcione localmente.

    A continuación se describen las variables más importantes:

    -   `APP_ENVIRONMENT`: Define el entorno de la aplicación (e.g., `development`, `production`).
    -   `APP_DEBUG`: Poner en `true` para activar el modo de depuración de Flask.
    -   `LOG_LEVEL`: Nivel de los logs (e.g., `DEBUG`, `INFO`).
    -   `DATABASE_HOST`: Host de la base de datos (apunta a `localhost` o `127.0.0.1` para Docker).
    -   `DATABASE_PORT`: Puerto de la base de datos.
    -   `DATABASE_USER`: Usuario para la conexión.
    -   `DATABASE_PASSWORD`: Contraseña para la conexión.
    -   `DATABASE_NAME`: Nombre de la base de datos.

---

## 4. Base de Datos con Docker

Para evitar instalar MySQL directamente en tu máquina, usamos Docker para levantar un contenedor con la base de datos.

1.  **Navega al directorio de Docker**:
    ```bash
    cd local/docker
    ```

2.  **Levanta el servicio**:
    ```bash
    docker-compose up -d
    ```
    El flag `-d` ejecuta el contenedor en segundo plano (detached mode).

Para verificar que el contenedor está corriendo, puedes usar el comando:
```bash
docker ps
```
Deberías ver un contenedor llamado `accounting-mysql` en la lista.

---

Una vez que el entorno esté configurado, sigue la [Guía de Ejecución Local](./local-run.md) para iniciar la aplicación. 