# Arquitectura del Task Manager Contable

Este documento proporciona una visión general de alto nivel de la arquitectura de software utilizada en el **Task Manager Contable**. El sistema está diseñado para gestionar tareas contables de manera eficiente siguiendo principios de Clean Architecture.

## El Modelo de Arquitectura Limpia (Clean Architecture)

Este proyecto se basa en los principios de **Clean Architecture**, popularizados por Robert C. Martin (Uncle Bob). Esta elección no es arbitraria; se hizo para cumplir con objetivos de negocio y técnicos clave:

-   **Independencia del Framework**: El núcleo de la lógica de negocio no depende de frameworks externos como Flask. Esto nos permite cambiar o actualizar el framework con un impacto mínimo en las reglas de negocio.
-   **Capacidad de Prueba (Testability)**: Las reglas de negocio se pueden probar sin necesidad de una base de datos, una interfaz de usuario o cualquier elemento externo. Esto hace que las pruebas sean más rápidas, sencillas y fiables.
-   **Independencia de la Interfaz de Usuario**: La lógica de negocio no se ve afectada por los cambios en la interfaz de usuario (por ejemplo, cambiar de una API REST a una interfaz de línea de comandos).
-   **Independencia de la Base de Datos**: Podemos cambiar de motor de base de datos (por ejemplo, de MySQL a PostgreSQL) sin afectar las reglas de negocio.

### La Regla de la Dependencia

El principio más importante de Clean Architecture es la **Regla de la Dependencia**. Esta regla establece que las dependencias del código fuente solo pueden apuntar hacia adentro.

```text
+-------------------------------------------------------+
|  Infrastructure (Frameworks, DB, UI)                  |
| +---------------------------------------------------+ |
| |  Application (Use Cases)                          | |
| | +-----------------------------------------------+ | |
| | |  Domain (Entities, Business Rules)            | | |
| | +-----------------------------------------------+ | |
| +---------------------------------------------------+ |
+-------------------------------------------------------+

---------------------> Dependencia <----------------------
```

-   **Círculos Internos**: No saben nada sobre los círculos externos. Por ejemplo, el Dominio no sabe qué base de datos se está utilizando.
-   **Círculos Externos**: Son responsables de implementar los detalles técnicos. Por ejemplo, la capa de Infraestructura implementa los repositorios de la base de datos.

## Estructura de Capas en Este Proyecto

Para implementar Clean Architecture, hemos dividido el sistema en tres capas principales, que se corresponden con los círculos del diagrama:

1.  **Capa de Dominio (`domain/`)**: El núcleo del sistema. Contiene las entidades, las reglas de negocio y las interfaces (gateways) que definen cómo el dominio interactúa con el mundo exterior. Es completamente independiente de cualquier tecnología.

2.  **Capa de Aplicación (`application/`)**: Orquesta el flujo de datos. Contiene los casos de uso, que son los que ejecutan la lógica de negocio. Esta capa depende del Dominio, pero no de la Infraestructura.

3.  **Capa de Infraestructura (`infrastructure/`)**: Contiene todos los detalles técnicos y adaptadores al mundo exterior. Esto incluye la configuración de Flask, los controladores de la API REST, los repositorios de la base de datos y las implementaciones de otros servicios externos.

---

## Próximos Pasos

Para una descripción más detallada de cada una de estas capas y sus responsabilidades, consulta el documento [Detalle de Capas](./layers.md). 