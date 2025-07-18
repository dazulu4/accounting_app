"""
Configuración centralizada de la aplicación usando Pydantic Settings

¿Qué es pydantic-settings?
- Extensión de Pydantic para gestión de configuración
- Permite cargar configuración desde variables de entorno
- Valida automáticamente los tipos y valores
- Proporciona valores por defecto seguros
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class DatabaseSettings(BaseSettings):
    """
    Configuración de la base de datos
    
    ¿Qué hace BaseSettings?
    - Hereda de BaseModel pero está diseñado para configuración
    - Carga automáticamente valores desde variables de entorno
    - Convierte nombres de variables (DATABASE_HOST -> database_host)
    """
    
    # Configuración MySQL
    database_host: str = Field(default="localhost", description="Host de la base de datos")
    database_port: int = Field(default=3306, description="Puerto de la base de datos")
    database_name: str = Field(default="accounting", description="Nombre de la base de datos")
    database_user: str = Field(default="admin", description="Usuario de la base de datos")
    database_password: str = Field(default="admin", description="Contraseña de la base de datos")
    
    # Configuración de conexión
    database_pool_size: int = Field(default=10, description="Tamaño del pool de conexiones")
    database_max_overflow: int = Field(default=20, description="Máximo overflow del pool")
    database_echo: bool = Field(default=False, description="Mostrar queries SQL en logs")
    
    @property
    def database_url(self) -> str:
        """
        Construye la URL de conexión a la base de datos
        
        ¿Qué es @property?
        - Permite acceder a un método como si fuera un atributo
        - Se calcula dinámicamente cada vez que se accede
        - Útil para valores que dependen de otros campos
        """
        return f"mysql+aiomysql://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"


class APISettings(BaseSettings):
    """
    Configuración de la API
    """
    
    # Configuración del servidor
    api_host: str = Field(default="0.0.0.0", description="Host del servidor API")
    api_port: int = Field(default=8000, description="Puerto del servidor API")
    api_debug: bool = Field(default=False, description="Modo debug de la API")
    
    # Configuración de CORS
    cors_origins: list[str] = Field(default=["*"], description="Orígenes permitidos para CORS")
    cors_methods: list[str] = Field(default=["*"], description="Métodos HTTP permitidos")
    cors_headers: list[str] = Field(default=["*"], description="Headers permitidos")
    
    # Configuración de paginación
    default_page_size: int = Field(default=20, description="Tamaño de página por defecto")
    max_page_size: int = Field(default=100, description="Tamaño máximo de página")


class LoggingSettings(BaseSettings):
    """
    Configuración de logging
    """
    
    log_level: str = Field(default="INFO", description="Nivel de logging")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_file: Optional[str] = Field(default=None, description="Archivo de log (opcional)")


class Settings(BaseSettings):
    """
    Configuración principal que combina todas las configuraciones
    
    ¿Por qué usar composición?
    - Organiza la configuración por áreas
    - Facilita el mantenimiento
    - Permite reutilizar configuraciones en diferentes contextos
    """
    
    # Configuraciones específicas
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    api: APISettings = Field(default_factory=APISettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    
    # Configuración general
    environment: str = Field(default="development", description="Entorno de ejecución")
    version: str = Field(default="1.0.0", description="Versión de la aplicación")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }


# Instancia global de configuración
# ¿Por qué una instancia global?
# - Se carga una sola vez al inicio de la aplicación
# - Es thread-safe y eficiente
# - Fácil de acceder desde cualquier parte del código
settings = Settings() 