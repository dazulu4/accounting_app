# Calidad del Código: Linting y Formateo

Para mantener un código limpio, legible y consistente en todo el proyecto, utilizamos un conjunto de herramientas de formateo y análisis estático. Es obligatorio que cualquier contribución pase estas verificaciones antes de ser integrada.

---

## 1. Formateo de Código

El formateo automático de código nos ahorra tiempo y evita debates sobre estilos.

### Black

-   **Propósito**: `black` es un formateador de código "sin concesiones". Reformatea automáticamente el código para que siga un estilo único y consistente.
-   **Uso**:
    ```bash
    # Para formatear todo el proyecto
    poetry run black .
    ```

### isort

-   **Propósito**: `isort` ordena y agrupa las importaciones en los archivos Python. Esto mejora la legibilidad y evita problemas de importaciones circulares.
-   **Uso**:
    ```bash
    # Para ordenar las importaciones en todo el proyecto
    poetry run isort .
    ```

---

## 2. Análisis Estático (Linting)

El linting nos ayuda a detectar errores comunes y malas prácticas antes de que el código se ejecute.

### Flake8

-   **Propósito**: `flake8` es un linter que combina varias herramientas para verificar el cumplimiento del estándar **PEP 8**, detectar errores lógicos y analizar la complejidad del código.
-   **Uso**:
    ```bash
    # Para analizar todo el proyecto
    poetry run flake8
    ```

### MyPy

-   **Propósito**: `mypy` es un verificador de tipos estáticos. Analiza las anotaciones de tipo (`type hints`) en el código para encontrar errores de tipo, lo que ayuda a prevenir bugs en tiempo de ejecución.
-   **Uso**:
    ```bash
    # Para verificar los tipos en todo el proyecto
    poetry run mypy .
    ```

---

## 3. Verificación Completa

Para facilitar el proceso, puedes ejecutar todas las verificaciones de calidad (excepto el formateo automático) con los siguientes comandos. Estos son los mismos que se ejecutan en el pipeline de CI.

```bash
# Verificar formateo sin aplicar cambios
poetry run black . --check
poetry run isort . --check-only

# Ejecutar linters
poetry run flake8
poetry run mypy .
```

Asegúrate de que todos estos comandos se ejecuten sin errores antes de enviar un Pull Request.

---

Para saber cómo ejecutar las pruebas automatizadas, consulta la [Estrategia de Pruebas](./testing.md). 