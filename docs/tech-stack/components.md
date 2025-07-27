# Stack Tecnológico - Task Manager Contable

Este documento describe las principales herramientas, librerías y frameworks que componen el stack tecnológico del **Task Manager Contable**.

---

## Backend

| Componente | Descripción |
| :--- | :--- |
| **Python** | El lenguaje de programación principal utilizado para todo el backend. |
| **Flask** | Un micro-framework web ligero para construir la API REST. Se utiliza principalmente en la capa de `Infrastructure`. |
| **Poetry** | El gestor de dependencias y empaquetado del proyecto. Gestiona el entorno virtual y las librerías. |

---

## Base de Datos y ORM

| Componente | Descripción |
| :--- | :--- |
| **MySQL 8** | El motor de base de datos relacional utilizado para la persistencia de datos. |
| **SQLAlchemy** | El ORM (Object-Relational Mapper) principal. Se utiliza para mapear las entidades del dominio a tablas de la base de datos. |
| **Alembic** | La herramienta de migración de bases de datos para SQLAlchemy. Permite gestionar los cambios en el esquema de la base de datos de forma versionada. |
| **Pydantic** | Librería de validación de datos. Se utiliza para definir los `schemas` que validan los datos de entrada y salida de la API, y para definir las entidades del dominio. |

---

## Calidad de Código y Pruebas

| Componente | Descripción |
| :--- | :--- |
| **Pytest** | El framework de pruebas utilizado para escribir y ejecutar pruebas unitarias y de integración. |
| **Pytest-Cov** | Un plugin para `pytest` que mide la cobertura de código de las pruebas. |
| **Black** | Un formateador de código automático que asegura un estilo de código consistente. |
| **isort** | Una utilidad para ordenar automáticamente las importaciones en los archivos Python. |
| **Flake8** | Un linter que comprueba el código en busca de errores y problemas de estilo, siguiendo el estándar PEP 8. |
| **MyPy** | Un verificador de tipos estáticos que ayuda a encontrar errores de tipo antes de la ejecución. |

---

## Entorno de Desarrollo

| Componente | Descripción |
| :--- | :--- |
| **Docker** | Se utiliza para crear un entorno de desarrollo consistente, principalmente para levantar la base de datos MySQL. |
| **Git** | El sistema de control de versiones distribuido para gestionar el código fuente. |
| **GitHub** | La plataforma de hosting para el repositorio de Git y para la colaboración en equipo. |

---

Para consultar las versiones específicas de estas herramientas, consulta el documento de [Versiones del Stack Tecnológico](./versions.md). 