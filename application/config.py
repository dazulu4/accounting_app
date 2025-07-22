"""
Configuración Centralizada - Edición Simplificada

Este módulo utiliza Pydantic Settings para gestionar la configuración de la
aplicación de forma centralizada, validada y cargada desde variables de entorno.

Características:
- Carga desde archivo .env y variables de entorno.
- Validación de tipos para evitar errores de configuración.
- Estructura anidada para una mejor organización.
- Limitado a los entornos 'development' y 'production'.
"""

import enum
from pydantic_settings import BaseSettings
from pydantic import Field

# Enum para los entornos soportados
class AppEnvironment(str, enum.Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class DatabaseSettings(BaseSettings):
    """Configuración específica para la base de datos."""
    username: str = Field(..., env="DATABASE_USERNAME")
    password: str = Field(..., env="DATABASE_PASSWORD")
    host: str = Field(..., env="DATABASE_HOST")
    port: int = Field(..., env="DATABASE_PORT")
    name: str = Field(..., env="DATABASE_NAME")

    class Config:
        env_prefix = "DB_" # Prefijo para variables de entorno (ej. DB_HOST)


class ApplicationSettings(BaseSettings):
    """Configuración general de la aplicación."""
    environment: AppEnvironment = Field(AppEnvironment.DEVELOPMENT, env="APP_ENVIRONMENT")
    debug: bool = Field(False, env="APP_DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    version: str = "2.0.0" # Versión de la aplicación


class Settings(BaseSettings):
    """
    Configuración principal que agrupa todas las demás.
    
    Pydantic cargará automáticamente las variables de un archivo .env
    y luego las sobreescribirá con cualquier variable de entorno del sistema
    que coincida.
    """
    application: ApplicationSettings = Field(default_factory=ApplicationSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)

    class Config:
        # Configura pydantic-settings para leer un archivo .env
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Permite anidar configuraciones
        env_nested_delimiter = '__'


# Instancia global y única de la configuración.
# Se carga una sola vez al inicio y se importa en el resto de la aplicación.
settings = Settings() 