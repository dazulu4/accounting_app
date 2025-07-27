# Versiones del Stack Tecnológico

Este documento especifica las versiones exactas de todas las herramientas y librerías utilizadas en el **Task Manager Contable**. Estas versiones están fijadas en el archivo `poetry.lock` para garantizar la reproducibilidad del entorno.

---

## Versiones Principales

### Lenguaje y Entorno
| Componente | Versión | Descripción |
| :--- | :--- | :--- |
| **Python** | `>=3.11,<3.14` | Versión del lenguaje de programación |
| **Poetry** | `1.8.0+` | Gestor de dependencias y empaquetado |

### Framework Web
| Componente | Versión | Descripción |
| :--- | :--- | :--- |
| **Flask** | `^3.1.1` | Micro-framework web |
| **Flask-CORS** | `^6.0.1` | Soporte para CORS en Flask |

### Base de Datos y ORM
| Componente | Versión | Descripción |
| :--- | :--- | :--- |
| **SQLAlchemy** | `^2.0.41` | ORM principal |
| **PyMySQL** | `^1.1.1` | Driver MySQL para Python |
| **Alembic** | `^1.16.4` | Herramienta de migraciones |

### Validación y Configuración
| Componente | Versión | Descripción |
| :--- | :--- | :--- |
| **Pydantic** | `^2.11.7` | Validación de datos con extras de email |
| **Pydantic-Settings** | `^2.10.1` | Gestión de configuración |

### Utilidades
| Componente | Versión | Descripción |
| :--- | :--- | :--- |
| **Structlog** | `^25.4.0` | Logging estructurado |
| **Python-dotenv** | `^1.1.1` | Carga de variables de entorno |
| **Cryptography** | `^45.0.5` | Utilidades criptográficas |

---

## Herramientas de Desarrollo

### Framework de Pruebas
| Componente | Versión | Descripción |
| :--- | :--- | :--- |
| **Pytest** | `^8.4.1` | Framework de pruebas |
| **Pytest-Cov** | `^4.1.0` | Plugin de cobertura |
| **Pytest-Mock** | `^3.12.0` | Plugin de mocking |

### Calidad de Código
| Componente | Versión | Descripción |
| :--- | :--- | :--- |
| **Black** | `^25.1.0` | Formateador de código |
| **isort** | `^6.0.1` | Ordenador de importaciones |
| **MyPy** | `^1.17.0` | Verificador de tipos estáticos |
| **Flake8** | `^7.3.0` | Linter de código |
| **Autoflake** | `^2.3.1` | Limpiador automático de imports |

---

## Configuración de Herramientas

### Black (Formateador)
- **Longitud de línea**: 88 caracteres
- **Versión objetivo**: Python 3.11
- **Excluye**: Directorios de build, cache, y migraciones

### isort (Ordenador de Imports)
- **Perfil**: Compatible con Black
- **Longitud de línea**: 88 caracteres
- **Salida multilínea**: Modo 3

### MyPy (Verificador de Tipos)
- **Versión de Python**: 3.11
- **Configuración**: Moderadamente permisiva
- **Cobertura de tipos**: 50% mínimo
- **Ignora imports faltantes**: Para librerías externas

### Pytest (Pruebas)
- **Cobertura mínima**: 50%
- **Marcadores**: `unit`, `database`
- **Rutas de prueba**: `tests/`

### Flake8 (Linter)
- **Longitud de línea**: 88 caracteres
- **Ignora**: E203, W503 (compatible con Black)
- **Excluye**: Directorios de build y cache

---

## Política de Actualización

### Actualizaciones Automáticas
- **Dependencias de desarrollo**: Se actualizan regularmente
- **Dependencias de producción**: Requieren revisión manual
- **Versiones críticas**: Se evalúan caso por caso

### Criterios de Actualización
1. **Seguridad**: Parches de seguridad se aplican inmediatamente
2. **Compatibilidad**: Se verifica que no rompan funcionalidad existente
3. **Mejoras**: Se evalúan beneficios vs. riesgo de cambios
4. **Pruebas**: Todas las actualizaciones requieren pasar las pruebas

### Proceso de Actualización
```bash
# Verificar dependencias obsoletas
poetry show --outdated

# Actualizar dependencias específicas
poetry update <package-name>

# Verificar que las pruebas pasen
poetry run pytest

# Verificar calidad del código
./scripts/quality.sh
```

---

## Compatibilidad

### Sistemas Operativos Soportados
- **Windows**: 10/11
- **macOS**: 12.0+
- **Linux**: Ubuntu 20.04+, CentOS 8+

### Entornos de Ejecución
- **Desarrollo**: Local con Poetry
- **Pruebas**: CI/CD con GitHub Actions
- **Producción**: AWS Lambda con Python 3.11

### Base de Datos
- **MySQL**: 8.0+
- **Docker**: MySQL 8.0 para desarrollo
- **Cloud**: Amazon RDS MySQL

---

Para consultar la configuración detallada de cada herramienta, revisa el archivo `pyproject.toml` en la raíz del proyecto. 