# Proceso de Despliegue

Este documento describe el proceso de despliegue de la aplicación, desde que un cambio se desarrolla en local hasta que llega a producción.

---

## Flujo General del Despliegue

```text
1. Desarrollo Local (rama feature/)
       |
       v
2. Pull Request a `develop`
       |
       v
3. Merge a `develop` (Dispara CI)
       |
       v
4. Despliegue a Producción (desde `master`)
```

---

## 1. Desarrollo en Local

-   Cada nueva funcionalidad se desarrolla en una rama `feature/`, siguiendo el [flujo de trabajo de Git](../git/workflow.md).
-   El desarrollador debe ejecutar las pruebas y validaciones de calidad localmente.

## 2. Integración Continua (CI)

-   Al abrir un Pull Request hacia `develop`, se dispara un pipeline de CI.
-   **Pasos del Pipeline de CI**:
    1.  Instalación de dependencias.
    2.  Ejecución de linters y formateadores.
    3.  Ejecución de pruebas automatizadas.
    4.  Análisis de cobertura.
-   El PR no se podrá mergear si alguno de estos pasos falla.

## 3. Despliegue a Producción

-   Periódicamente, los cambios de `develop` se integran en `master` a través de un Pull Request.
-   **El merge a `master` es el disparador para el despliegue a Producción**.
-   Un pipeline de Despliegue Continuo (CD) se encarga de empaquetar y desplegar la aplicación en el entorno de producción de AWS.

## 4. Migraciones en Producción

-   Las migraciones de la base de datos **no se ejecutan automáticamente**.
-   Deben ser ejecutadas de forma manual y controlada por un administrador.
-   **Comando**: `poetry run alembic upgrade head`

---

Para conocer los servicios de nube específicos que se utilizan, consulta el documento de [Infraestructura de Despliegue](./infrastructure.md). 