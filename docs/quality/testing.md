# Estrategia de Pruebas

Las pruebas automatizadas son un pilar fundamental de este proyecto para garantizar la calidad, la fiabilidad y la mantenibilidad del código. Utilizamos `pytest` como framework principal para escribir y ejecutar todas nuestras pruebas.

---

## Tipos de Pruebas

Nuestra estrategia de pruebas se divide en dos categorías principales:

### 1. Pruebas Unitarias (`tests/unit/`)

-   **Propósito**: Probar componentes individuales (una clase, una función) de forma aislada. Estas pruebas no deben tener dependencias externas como bases de datos o APIs.
-   **Ubicación**: `tests/unit/`
-   **Características**:
    -   Son rápidas de ejecutar.
    -   No requieren un entorno complejo.
    -   Cualquier dependencia externa se simula (mock). Por ejemplo, al probar un caso de uso, el gateway de la base de datos se reemplaza por un mock.
    -   Cubren entidades de dominio, casos de uso, y manejo de errores.

### 2. Pruebas de Integración (`tests/integration/`)

-   **Propósito**: Probar la interacción entre varios componentes del sistema. Por ejemplo, verificar el flujo completo desde una petición HTTP hasta la escritura en la base de datos.
-   **Ubicación**: `tests/integration/`
-   **Características**:
    -   Son más lentas que las pruebas unitarias.
    -   Requieren un entorno más completo (e.g., una base de datos de prueba).
    -   Son cruciales para asegurar que las diferentes partes del sistema funcionan bien juntas.
    -   Incluyen pruebas de endpoints HTTP y manejo de errores.

### 3. Cobertura de Pruebas

El sistema mantiene una cobertura de pruebas del **50%** como mínimo, con énfasis en:

- **Entidades de dominio**: Validación de reglas de negocio
- **Casos de uso**: Lógica de aplicación
- **Manejo de errores**: Sistema centralizado de errores
- **Validación de datos**: Esquemas Pydantic

---

## Cómo Ejecutar las Pruebas

Puedes ejecutar todas las pruebas utilizando el siguiente comando desde la raíz del proyecto:

```bash
poetry run pytest
```

`pytest` descubrirá y ejecutará automáticamente todos los archivos de prueba (que siguen el patrón `test_*.py`) en el directorio `tests/`.

### Ejecutar un Subconjunto de Pruebas

Si solo quieres ejecutar un tipo específico de pruebas, puedes usar los marcadores (`markers`) que hemos definido:

-   **Ejecutar solo pruebas unitarias**:
    ```bash
    poetry run pytest -m unit
    ```

-   **Ejecutar solo pruebas de integración (que acceden a la base de datos)**:
    ```bash
    poetry run pytest -m database
    ```

---

## Escribir Nuevas Pruebas

Cuando añadas una nueva funcionalidad, debes acompañarla de las pruebas correspondientes.

-   **Nuevos Casos de Uso**: Deben tener pruebas unitarias que verifiquen su lógica de negocio.
-   **Nuevos Endpoints**: Deben tener pruebas de integración que verifiquen el flujo completo de la petición.

Sigue la estructura de directorios existente en `tests/` para organizar tus nuevas pruebas.

---

Para medir qué tan efectivas son tus pruebas, consulta el documento de [Análisis de Cobertura de Código](./coverage.md). 