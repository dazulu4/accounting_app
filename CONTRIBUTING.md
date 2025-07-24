# Pautas para Contribuir al Proyecto

¡Antes que nada, gracias por considerar contribuir a este proyecto! Agradecemos cualquier ayuda que puedas proporcionar. Siguiendo estas pautas, nos ayudarás a mantener la calidad del código y la eficiencia del proceso de desarrollo.

## Tabla de Contenidos

- [Pautas para Contribuir al Proyecto](#pautas-para-contribuir-al-proyecto)
  - [Tabla de Contenidos](#tabla-de-contenidos)
  - [Cómo Empezar](#cómo-empezar)
  - [Flujo de Trabajo con Git](#flujo-de-trabajo-con-git)
  - [Estándares de Código](#estándares-de-código)
  - [Proceso de Pull Request](#proceso-de-pull-request)
  - [Ejecución de Pruebas](#ejecución-de-pruebas)

---

## Cómo Empezar

Antes de comenzar, asegúrate de haber seguido todos los pasos de la [Guía de Inicio Rápido](README.md#guía-de-inicio-rápido) en el archivo `README.md`. Esto incluye:

1.  **Hacer un fork** del repositorio en GitHub.
2.  **Clonar tu fork** a tu máquina local.
3.  **Instalar las dependencias** con `poetry install`.
4.  **Configurar la base de datos** con Docker.

---

## Flujo de Trabajo con Git

Este proyecto utiliza una versión simplificada del modelo de ramificación **Git Flow**. Esto nos ayuda a mantener el desarrollo organizado y a separar las nuevas funcionalidades del código estable.

### Ramas Principales

-   `master`: Contiene el código de producción. Nadie debe hacer commits directamente a esta rama.
-   `develop`: Es la rama principal de desarrollo donde se integran las nuevas funcionalidades.

### Ramas de Soporte

-   **Ramas de Funcionalidad (`feature/`)**: Para desarrollar nuevas funcionalidades. Nacen de `develop` y vuelven a `develop` a través de un Pull Request.
-   **Ramas de Corrección (`hotfix/`)**: Para corregir errores críticos en producción. Nacen de `master` y se fusionan tanto a `master` como a `develop`.

Para más detalles, puedes consultar la [documentación completa del flujo de trabajo con Git](./docs/git/workflow.md).

---

## Estándares de Código

Para mantener la calidad y la consistencia del código, utilizamos las siguientes herramientas. Antes de enviar un Pull Request, por favor, asegúrate de que tu código cumpla con estos estándares.

-   **Formateo**: Usamos `black` para el formateo de código y `isort` para la ordenación de importaciones.
-   **Linting**: `flake8` se utiliza para comprobar errores de estilo.
-   **Tipado Estático**: `mypy` se utiliza para la comprobación estática de tipos.

Puedes ejecutar estas comprobaciones con los siguientes comandos:

```bash
# Formatear tu código
poetry run black .
poetry run isort .

# Ejecutar linters y comprobación de tipos
poetry run flake8
poetry run mypy .
```

Para más detalles, consulta la [documentación de Calidad del Código](./docs/quality/linting.md).

---

## Proceso de Pull Request

1.  **Crea un Pull Request (PR)** desde tu rama `feature/` a la rama `develop`.
2.  **Proporciona un título y una descripción claros** para tu PR. Explica el "qué" y el "porqué" de tus cambios. Si soluciona un issue existente, enlázalo.
3.  **Asegúrate de que todas las comprobaciones automáticas pasen** (CI, linting, tests).
4.  **Solicita una revisión** de al menos un miembro del equipo.
5.  **Atiende cualquier comentario** de los revisores. Una vez que tu PR sea aprobado, será mergeado por un mantenedor.

---

## Ejecución de Pruebas

Toda nueva funcionalidad debe ir acompañada de pruebas. El proyecto utiliza `pytest` para las pruebas.

-   **Pruebas Unitarias**: Prueban componentes individuales de forma aislada.
-   **Pruebas de Integración**: Prueban la interacción entre múltiples componentes.

Puedes ejecutar todas las pruebas con el siguiente comando:

```bash
poetry run pytest
```

Asegúrate de que la cobertura de código no disminuya después de tus cambios. Puedes comprobar la cobertura con:

```bash
poetry run pytest --cov
```

Para más detalles, consulta la [documentación sobre la Estrategia de Pruebas](./docs/quality/testing.md).

---

¡Gracias por tu colaboración! 