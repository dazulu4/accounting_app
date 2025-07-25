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
    -   `DATABASE_HOST`: Host de la base de datos (apunta a `127.0.0.1` para Docker).
    -   `DATABASE_PORT`: Puerto de la base de datos.
    -   `DATABASE_USERNAME`: Usuario para la conexión.
    -   `DATABASE_PASSWORD`: Contraseña para la conexión.
    -   `DATABASE_NAME`: Nombre de la base de datos.
    -   `CORS_ORIGINS`: Orígenes permitidos para peticiones a la API.

---

## 4. Base de Datos

La aplicación requiere una base de datos MySQL para funcionar. Tienes dos opciones principales para configurar esto en tu entorno local.

### Opción 1: Usar Docker (Recomendado)

Esta es la forma más rápida y sencilla de empezar, ya que no requiere instalar MySQL en tu máquina.

1.  **Requisito**: Tener Docker y Docker Compose instalados.
2.  **Levantar el servicio**:
    ```bash
    docker-compose -f local/docker/docker-compose.yml up -d
    ```
    Este comando utiliza el archivo de configuración en `local/docker` para crear y ejecutar un contenedor con una base de datos MySQL lista para ser usada. El flag `-d` lo ejecuta en segundo plano.

### Opción 2: Usar una Instalación Local de MySQL

Si prefieres no usar Docker o ya tienes MySQL instalado en tu máquina, puedes usar esa instancia.

1.  **Asegúrate de que MySQL esté corriendo**.
2.  **Crea una base de datos** para la aplicación si aún no existe. Por defecto, la aplicación buscará una base de datos llamada `accounting`.
    ```sql
    CREATE DATABASE accounting;
    ```
3.  **Configura tu archivo `.env`** con los datos de conexión correctos (host, puerto, usuario y contraseña) para que apunten a tu instancia local de MySQL.

---

Una vez que el entorno esté configurado, sigue la [Guía de Ejecución Local](./local-run.md) para iniciar la aplicación. 