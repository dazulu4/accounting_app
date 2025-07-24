# Flujo de Trabajo con Git

Este proyecto utiliza una versión simplificada del modelo de ramificación **Git Flow** para gestionar el ciclo de vida del desarrollo.

---

## Ramas Principales

Existen dos ramas principales que tienen un ciclo de vida infinito:

-   `master`: Esta rama representa el código que está en **Producción**. Siempre debe estar estable y lista para ser desplegada. Nadie debe hacer `commit` directamente a `master`.
-   `develop`: Esta es la rama principal de **desarrollo**. Integra todas las nuevas funcionalidades que han sido completadas.

---

## Ramas de Soporte

### 1. Ramas de Funcionalidad (`feature/`)

-   **Propósito**: Desarrollar nuevas funcionalidades.
-   **Se ramifican desde**: `develop`.
-   **Se fusionan a**: `develop`.
-   **Convención de Nombre**: `feature/<nombre-descriptivo>` (e.g., `feature/user-authentication`).

**Flujo de trabajo**:
1.  `git checkout develop`
2.  `git checkout -b feature/new-feature`
3.  ... (desarrollo y commits) ...
4.  Crear un Pull Request de `feature/new-feature` a `develop`.

### 2. Ramas de Corrección (`hotfix/`)

-   **Propósito**: Corregir errores críticos que se encuentran en producción.
-   **Se ramifican desde**: `master`.
-   **Se fusionan a**: `master` y `develop`.
-   **Convención de Nombre**: `hotfix/<descripcion-corta>` (e.g., `hotfix/fix-login-bug`).

**Flujo de trabajo**:
1.  `git checkout master`
2.  `git checkout -b hotfix/fix-login-bug`
3.  ... (corrección del error) ...
4.  Merge a `master` (y se etiqueta con una nueva versión de parche).
5.  Merge de vuelta a `develop`.

---

## Proceso de Pull Request (PR)

-   **Todo el trabajo debe ser integrado a través de Pull Requests**. No se permiten commits directos a `develop` o `master`.
-   Un PR debe ser revisado y aprobado por al menos otro miembro del equipo.
-   Todos los checks de CI (pruebas, linting, etc.) deben pasar antes de que un PR pueda ser mergeado. 