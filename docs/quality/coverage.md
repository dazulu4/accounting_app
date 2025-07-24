# Análisis de Cobertura de Código

La cobertura de código es una métrica que nos ayuda a medir qué porcentaje de nuestro código fuente se ejecuta durante las pruebas. Aunque una cobertura del 100% no garantiza la ausencia de errores, una cobertura baja es una señal de que hay partes importantes del sistema que no se están probando.

En este proyecto, utilizamos `pytest-cov`, un plugin de `pytest`, para generar informes de cobertura.

---

## Cómo Generar el Informe de Cobertura

Para generar un informe de cobertura en la terminal, puedes ejecutar el siguiente comando:

```bash
poetry run pytest --cov
```

Este comando ejecutará todas las pruebas y, al final, mostrará un resumen de la cobertura en la consola, similar a este:

```
---------- coverage: platform linux, python 3.11.2-final-0 -----------
Name                                      Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------
domain/entities/task_entity.py               15      0   100%
domain/usecases/create_task_use_case.py      10      1    90%   15
...
-----------------------------------------------------------------------
TOTAL                                       150     10    93%
```

### Umbral de Cobertura

Hemos configurado un umbral mínimo de cobertura del **50%**. Si la cobertura total del proyecto cae por debajo de este umbral, las pruebas fallarán. Esto nos obliga a mantener un nivel mínimo de pruebas para todo el código nuevo que se añada.

---

## Informe de Cobertura en HTML

Para un análisis más detallado, puedes generar un informe de cobertura en formato HTML. Este informe te permite navegar por los archivos y ver exactamente qué líneas de código no están cubiertas por las pruebas.

Para generar el informe HTML, ejecuta:

```bash
poetry run pytest --cov --cov-report=html
```

Esto creará un directorio `htmlcov/` en la raíz del proyecto. Para ver el informe, abre el archivo `htmlcov/index.html` en tu navegador.

---

## Qué Medimos (y Qué No)

La configuración de la cobertura en `pyproject.toml` está ajustada para medir solo el código relevante:

-   **Directorios Incluidos**: `domain`, `infrastructure`.
-   **Archivos Omitidos**: Archivos de inicialización (`__init__.py`), migraciones, scripts y pruebas.

El objetivo es centrar el análisis de cobertura en la lógica de negocio y las implementaciones de infraestructura, que son las partes más críticas del sistema. 