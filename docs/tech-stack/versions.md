# Versiones del Stack Tecnológico

Este documento proporciona una tabla de referencia con las versiones específicas de las herramientas y librerías clave utilizadas en el proyecto. Mantener un registro de las versiones es crucial para la reproducibilidad del entorno y para evitar conflictos de compatibilidad.

La fuente de verdad para todas las dependencias y sus versiones es el archivo `poetry.lock`.

---

## Versiones Principales

| Componente | Versión | Notas |
| :--- | :--- | :--- |
| **Python** | `>=3.11, <3.14` | Versión base del lenguaje. |
| **Flask** | `^3.1.1` | Framework web. |
| **SQLAlchemy**| `^2.0.41` | ORM para la base de datos. |
| **Alembic** | `^1.16.4` | Herramienta de migración de DB. |
| **Pydantic** | `^2.11.7` | Librería de validación de datos. |
| **Pytest** | `^8.4.1` | Framework de pruebas. |
| **Docker** | `(No especificada)`| Se recomienda usar una versión reciente y estable. |
| **MySQL** | `8.0` | Versión utilizada en el contenedor de Docker. |

---

## Herramientas de Calidad de Código

| Componente | Versión |
| :--- | :--- |
| **Black** | `^25.1.0` |
| **isort** | `^6.0.1` |
| **Flake8** | `^7.3.0` |
| **MyPy** | `^1.17.0` |

---

> El símbolo `^` (caret) en las versiones indica que `poetry` puede instalar actualizaciones menores y de parches que sean compatibles con la versión especificada, pero no actualizaciones mayores (major) que puedan romper la compatibilidad. 