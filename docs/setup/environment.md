# Configuración del Entorno de Desarrollo

Este documento describe en detalle los requisitos y la configuración necesaria para levantar el entorno de desarrollo local del **Task Manager Contable**.

---

## 1. Requisitos de Software

Asegúrate de tener instaladas las siguientes herramientas en tu sistema:

### Herramientas Principales
- **Python**: Se requiere una versión `>=3.11` y `<3.14`. Puedes verificar tu versión con `python --version`.
- **Poetry**: Es el gestor de dependencias del proyecto. Si no lo tienes, sigue las [instrucciones oficiales de instalación](https://python-poetry.org/docs/#installation).
- **Git**: El sistema de control de versiones.

### Herramientas Opcionales (Recomendadas)
- **Docker y Docker Compose**: Necesarios para levantar la base de datos MySQL de forma aislada.
- **VS Code**: Editor recomendado con extensiones para Python y Flask.

---

## 2. Instalación de Dependencias

Una vez que hayas clonado el repositorio, el siguiente paso es instalar todas las dependencias de Python que el proyecto necesita. `Poetry` se encarga de esto de manera muy sencilla.

Desde la raíz del proyecto, ejecuta:

```bash
# Activar el entorno virtual (si es necesario)
poetry env activate

# Instalar todas las dependencias
poetry install
```

Este comando hará dos cosas:
1. **Creará un entorno virtual** específico para este proyecto, para aislar sus dependencias.
2. **Instalará todas las librerías** listadas en el archivo `pyproject.toml` (y fijadas en `poetry.lock`).

### Verificar la Instalación

Para verificar que todo se instaló correctamente:

```bash
# Verificar que Poetry está funcionando
poetry --version

# Verificar que las dependencias están instaladas
poetry show

# Verificar que puedes ejecutar Python
poetry run python --version
```

---

## 3. Variables de Entorno

La aplicación se configura mediante variables de entorno, siguiendo las mejores prácticas de [The Twelve-Factor App](https://12factor.net/config).

### Archivo `.env`

Para el desarrollo local, estas variables se gestionan a través de un archivo `.env` en la raíz del proyecto.

1. **Copia el archivo de ejemplo**:
    ```bash
    cp env.example .env
    ```

2. **Contenido del `.env`**:
    El archivo `.env` ya viene pre-configurado con los valores necesarios para conectarse a la base de datos que se levanta con Docker. No deberías necesitar cambiar nada para que la aplicación funcione localmente.

### Variables de Entorno Principales

#### Configuración de la Aplicación
| Variable | Valor por Defecto | Descripción |
| :--- | :--- | :--- |
| `APP_ENVIRONMENT` | `development` | Define el entorno de la aplicación |
| `APP_DEBUG` | `true` | Activa el modo de depuración de Flask |
| `APP_HOST` | `127.0.0.1` | Host donde se ejecuta la aplicación |
| `APP_PORT` | `8000` | Puerto donde se ejecuta la aplicación |

#### Configuración de Logging
| Variable | Valor por Defecto | Descripción |
| :--- | :--- | :--- |
| `LOG_LEVEL` | `DEBUG` | Nivel de los logs (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FORMAT` | `json` | Formato de los logs (json, text) |

#### Configuración de Base de Datos
| Variable | Valor por Defecto | Descripción |
| :--- | :--- | :--- |
| `DATABASE_HOST` | `127.0.0.1` | Host de la base de datos |
| `DATABASE_PORT` | `3306` | Puerto de la base de datos |
| `DATABASE_USERNAME` | `root` | Usuario para la conexión |
| `DATABASE_PASSWORD` | `password` | Contraseña para la conexión |
| `DATABASE_NAME` | `accounting` | Nombre de la base de datos |
| `DATABASE_URL` | `mysql+pymysql://root:password@127.0.0.1:3306/accounting` | URL completa de conexión |

#### Configuración de CORS
| Variable | Valor por Defecto | Descripción |
| :--- | :--- | :--- |
| `CORS_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | Orígenes permitidos para CORS |

#### Configuración de Seguridad
| Variable | Valor por Defecto | Descripción |
| :--- | :--- | :--- |
| `SECRET_KEY` | `dev-secret-key-change-in-production` | Clave secreta para la aplicación |
| `JWT_SECRET_KEY` | `jwt-secret-key-change-in-production` | Clave para tokens JWT |

---

## 4. Base de Datos

La aplicación requiere una base de datos MySQL para funcionar. Tienes dos opciones principales para configurar esto en tu entorno local.

### Opción 1: Usar Docker (Recomendado)

Esta es la forma más rápida y sencilla de empezar, ya que no requiere instalar MySQL en tu máquina.

1. **Requisito**: Tener Docker y Docker Compose instalados.
2. **Levantar el servicio**:
    ```bash
    docker-compose -f local/docker/docker-compose.yml up -d
    ```
    Este comando utiliza el archivo de configuración en `local/docker` para crear y ejecutar un contenedor con una base de datos MySQL lista para ser usada. El flag `-d` lo ejecuta en segundo plano.

3. **Verificar que la base de datos esté funcionando**:
    ```bash
    # Verificar que el contenedor está corriendo
    docker ps

    # Conectar a la base de datos para verificar
    docker exec -it accounting_mysql mysql -u root -ppassword
    ```

### Opción 2: Usar una Instalación Local de MySQL

Si prefieres no usar Docker o ya tienes MySQL instalado en tu máquina, puedes usar esa instancia.

1. **Asegúrate de que MySQL esté corriendo**.
2. **Crea una base de datos** para la aplicación si aún no existe. Por defecto, la aplicación buscará una base de datos llamada `accounting`.
    ```sql
    CREATE DATABASE accounting;
    ```
3. **Configura tu archivo `.env`** con los datos de conexión correctos (host, puerto, usuario y contraseña) para que apunten a tu instancia local de MySQL.

### Verificar la Conexión

Para verificar que la conexión a la base de datos funciona:

```bash
# Probar la conexión
poetry run python -c "from infrastructure.helpers.database.connection import get_database_url; print(get_database_url())"
```

---

## 5. Configuración por Entorno

### Desarrollo (Development)
- **Base de datos**: MySQL local con Docker
- **Logging**: Nivel DEBUG con formato JSON
- **CORS**: Orígenes locales permitidos
- **Debug**: Habilitado para desarrollo

### Pruebas (Testing)
- **Base de datos**: Base de datos de pruebas separada
- **Logging**: Nivel INFO
- **Debug**: Deshabilitado
- **Variables específicas**: Configuradas para pruebas

### Producción (Production)
- **Base de datos**: Amazon RDS MySQL
- **Logging**: Nivel INFO/WARNING
- **CORS**: Orígenes específicos de producción
- **Debug**: Deshabilitado
- **Seguridad**: Claves secretas fuertes

---

## 6. Verificación del Entorno

Una vez configurado el entorno, puedes verificar que todo funciona correctamente:

```bash
# Verificar que las dependencias están instaladas
poetry run python -c "import flask, sqlalchemy, pydantic; print('✅ Dependencias instaladas correctamente')"

# Verificar la configuración
poetry run python -c "from application.config.environment import get_settings; print('✅ Configuración cargada correctamente')"

# Verificar la conexión a la base de datos
poetry run python -c "from infrastructure.helpers.database.connection import get_database_url; print(f'✅ URL de BD: {get_database_url()}')"
```

---

## 7. Solución de Problemas Comunes

### Problema: Poetry no encuentra Python
```bash
# Solución: Especificar la versión de Python
poetry env use python3.11
```

### Problema: No se puede conectar a la base de datos
```bash
# Verificar que Docker está corriendo
docker ps

# Verificar que el contenedor MySQL está activo
docker logs accounting_mysql

# Verificar las variables de entorno
cat .env | grep DATABASE
```

### Problema: Dependencias no se instalan
```bash
# Limpiar cache de Poetry
poetry cache clear --all pypi

# Reinstalar dependencias
poetry install --sync
```

---

Una vez que el entorno esté configurado, sigue la [Guía de Ejecución Local](./local-run.md) para iniciar la aplicación. 