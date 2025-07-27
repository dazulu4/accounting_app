# Stack Tecnológico - Task Manager Contable

Este documento describe las principales herramientas, librerías y frameworks que componen el stack tecnológico del **Task Manager Contable**, explicando su propósito específico en el contexto de Clean Architecture.

---

## Backend y Framework Web

| Componente | Propósito en el Proyecto | Ubicación |
| :--- | :--- | :--- |
| **Python 3.11+** | Lenguaje de programación principal. Versión optimizada para rendimiento y características modernas. | Todo el proyecto |
| **Flask 3.1.1** | Micro-framework web para construir la API REST. Se utiliza principalmente en la capa de `Infrastructure` como adaptador HTTP. | `infrastructure/entrypoints/http/` |
| **Flask-CORS 6.0.1** | Middleware para habilitar CORS (Cross-Origin Resource Sharing) en la API. Permite peticiones desde frontends web. | Configuración global |
| **Poetry** | Gestor de dependencias y empaquetado del proyecto. Gestiona el entorno virtual y las librerías de forma reproducible. | Configuración del proyecto |

---

## Base de Datos y Persistencia

| Componente | Propósito en el Proyecto | Ubicación |
| :--- | :--- | :--- |
| **MySQL 8.0+** | Motor de base de datos relacional para persistencia de datos. Optimizado para transacciones ACID. | Base de datos |
| **SQLAlchemy 2.0.41** | ORM (Object-Relational Mapper) principal. Se utiliza para mapear las entidades del dominio a tablas de la base de datos. | `infrastructure/driven_adapters/repositories/` |
| **PyMySQL 1.1.1** | Driver MySQL nativo para Python. Proporciona conexión directa y eficiente a MySQL. | Conexión de base de datos |
| **Alembic 1.16.4** | Herramienta de migración de bases de datos para SQLAlchemy. Permite gestionar cambios en el esquema de forma versionada. | `migration/` |

---

## Validación y Configuración

| Componente | Propósito en el Proyecto | Ubicación |
| :--- | :--- | :--- |
| **Pydantic 2.11.7** | Librería de validación de datos. Se utiliza para definir los `schemas` que validan los datos de entrada y salida de la API. | `application/schemas/` |
| **Pydantic-Settings 2.10.1** | Gestión de configuración basada en Pydantic. Permite validación automática de variables de entorno. | `application/config/` |

---

## Logging y Monitoreo

| Componente | Propósito en el Proyecto | Ubicación |
| :--- | :--- | :--- |
| **Structlog 25.4.0** | Sistema de logging estructurado para monitoreo y debugging empresarial. Proporciona logs JSON estructurados. | `infrastructure/helpers/logger/` |
| **Python-dotenv 1.1.1** | Carga de variables de entorno desde archivos `.env`. Sigue las mejores prácticas de 12-Factor App. | Configuración del entorno |

---

## Seguridad y Utilidades

| Componente | Propósito en el Proyecto | Ubicación |
| :--- | :--- | :--- |
| **Cryptography 45.0.5** | Utilidades criptográficas para encriptación, hashing y generación de tokens seguros. | Utilidades de seguridad |

---

## Framework de Pruebas

| Componente | Propósito en el Proyecto | Ubicación |
| :--- | :--- | :--- |
| **Pytest 8.4.1** | Framework de pruebas principal. Utilizado para escribir y ejecutar pruebas unitarias y de integración. | `tests/` |
| **Pytest-Cov 4.1.0** | Plugin para medir cobertura de código. Genera reportes detallados de cobertura. | Configuración de pruebas |
| **Pytest-Mock 3.12.0** | Plugin para facilitar el mocking en pruebas unitarias. Permite simular dependencias externas. | Pruebas unitarias |

---

## Herramientas de Calidad de Código

| Componente | Propósito en el Proyecto | Configuración |
| :--- | :--- | :--- |
| **Black 25.1.0** | Formateador de código automático. Asegura un estilo de código consistente en todo el proyecto. | `pyproject.toml` |
| **isort 6.0.1** | Ordenador automático de importaciones. Mantiene las importaciones organizadas y compatibles con Black. | `pyproject.toml` |
| **Flake8 7.3.0** | Linter que comprueba el código en busca de errores y problemas de estilo, siguiendo PEP 8. | `.flake8` |
| **MyPy 1.17.0** | Verificador de tipos estáticos que ayuda a encontrar errores de tipo antes de la ejecución. | `pyproject.toml` |
| **Autoflake 2.3.1** | Limpiador automático de imports no utilizados. Mantiene el código limpio. | Scripts de calidad |

---

## Entorno de Desarrollo

| Componente | Propósito en el Proyecto | Configuración |
| :--- | :--- | :--- |
| **Docker** | Creación de entornos de desarrollo consistentes, principalmente para levantar la base de datos MySQL. | `local/docker/` |
| **Docker Compose** | Orquestación de servicios de desarrollo. Facilita el levantamiento de la base de datos. | `local/docker/docker-compose.yml` |
| **Git** | Sistema de control de versiones distribuido para gestionar el código fuente. | Repositorio |
| **GitHub** | Plataforma de hosting para el repositorio de Git y para la colaboración en equipo. | CI/CD |

---

## Arquitectura y Patrones

### Clean Architecture
- **Domain Layer**: Entidades de negocio y reglas de negocio
- **Application Layer**: Casos de uso y orquestación
- **Infrastructure Layer**: Adaptadores externos (HTTP, Database, etc.)

### Patrones de Diseño
- **Repository Pattern**: Abstracción de acceso a datos
- **Use Case Pattern**: Lógica de aplicación encapsulada
- **Dependency Injection**: Inyección de dependencias
- **Factory Pattern**: Creación de objetos complejos

### Manejo de Errores
- **Centralized Error Handling**: Sistema centralizado de errores
- **HTTP Status Codes**: Códigos de estado apropiados
- **Structured Logging**: Logs estructurados para debugging

---

## Configuración por Entorno

### Desarrollo
- **Base de datos**: MySQL local con Docker
- **Logging**: Nivel DEBUG
- **CORS**: Orígenes locales permitidos
- **Pruebas**: Ejecución automática

### Producción
- **Base de datos**: Amazon RDS MySQL
- **Logging**: Nivel INFO/WARNING
- **CORS**: Orígenes específicos
- **Monitoreo**: Métricas y alertas

---

## Integración Continua

### GitHub Actions
- **Pruebas automáticas**: Ejecución en cada push
- **Análisis de calidad**: Black, isort, flake8, mypy
- **Cobertura de código**: Reportes automáticos
- **Despliegue**: Automatizado a AWS Lambda

---

Para consultar las versiones específicas de estas herramientas, consulta el documento de [Versiones del Stack Tecnológico](./versions.md). 