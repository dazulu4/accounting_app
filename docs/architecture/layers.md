# Detalle de las Capas de la Arquitectura

Este documento profundiza en cada una de las capas que componen el sistema, siguiendo el modelo de **Clean Architecture**. Cada capa tiene un propósito y unas responsabilidades bien definidas.

---

## 1. Capa de Dominio (`domain/`)

**Propósito**: Esta es la capa más interna y el corazón del sistema. Contiene la lógica de negocio pura y las reglas que son fundamentales para la aplicación, independientemente de la tecnología que se utilice.

**Reglas Clave**:
-   No depende de ninguna otra capa.
-   No conoce la base de datos, el framework web ni ninguna otra herramienta externa.
-   Define las políticas y el modelo de datos del negocio.

### Componentes Principales:

-   **Entidades (`domain/entities/`)**: Son los objetos de negocio principales (e.g., `User`, `Task`). Contienen los atributos y la lógica que es intrínseca a ellos. Por ejemplo, una entidad `Task` podría tener un método para marcarse como completada.

-   **Gateways (`domain/gateways/`)**: Son interfaces (contratos) que definen cómo el dominio se comunica con el mundo exterior. Por ejemplo, `TaskGateway` define métodos como `save(task)` o `find_by_id(task_id)`, pero no sabe cómo se implementan. La implementación real se encuentra en la capa de Infraestructura.

-   **Casos de Uso (`domain/usecases/`)**: Representan las acciones que un usuario puede realizar en el sistema (e.g., `CreateTaskUseCase`, `CompleteTaskUseCase`). Orquestan el flujo de trabajo, utilizando las entidades y los gateways para cumplir con un objetivo de negocio.

-   **Excepciones (`domain/exceptions/`)**: Excepciones personalizadas que representan errores de negocio específicos (e.g., `UserNotFoundError`, `TaskAlreadyCompletedError`).

---

## 2. Capa de Aplicación (`application/`)

**Propósito**: Esta capa actúa como un orquestador. Es responsable de iniciar la aplicación y de conectar las diferentes capas.

**Reglas Clave**:
-   Depende de la capa de Dominio.
-   No depende de la capa de Infraestructura, aunque la inicializa.
-   Contiene la configuración de la inyección de dependencias.

### Componentes Principales:

-   **`main.py`**: El punto de entrada de la aplicación. Aquí es donde se crea la instancia de Flask y se configuran las rutas.
-   **`container.py`**: El contenedor de inyección de dependencias. Se encarga de construir y proporcionar las implementaciones concretas de los gateways y casos de uso.
-   **Schemas (`application/schemas/`)**: Esquemas de validación de datos (Pydantic) que se utilizan para validar los datos de entrada y salida de la API.

---

## 3. Capa de Infraestructura (`infrastructure/`)

**Propósito**: Esta es la capa más externa. Contiene todos los detalles técnicos y las implementaciones concretas de las interfaces definidas en el dominio.

**Reglas Clave**:
-   Depende de la capa de Dominio (para implementar sus interfaces) y de la capa de Aplicación.
-   Es la única capa que conoce los frameworks, las bases de datos y otras herramientas externas.

### Componentes Principales:

-   **Entrypoints (`infrastructure/entrypoints/`)**: Los puntos de entrada al sistema desde el exterior.
    -   `http/`: Controladores de la API REST (rutas de Flask) que reciben peticiones HTTP, las validan y llaman a los casos de uso correspondientes.

-   **Driven Adapters (`infrastructure/driven_adapters/`)**: Implementaciones concretas de los gateways del dominio.
    -   `repositories/`: Repositorios que interactúan con la base de datos. Por ejemplo, `TaskRepository` implementa `TaskGateway` utilizando SQLAlchemy para persistir los datos en MySQL.

-   **Helpers (`infrastructure/helpers/`)**: Clases de utilidad para tareas comunes de infraestructura.
    -   `database/`: Configuración de la conexión a la base de datos y la unidad de trabajo (Unit of Work).
    -   `logger/`: Configuración del sistema de logging.
    -   `errors/`: Manejadores de errores globales.
    -   `middleware/`: Middleware HTTP.

---

## Flujo de una Petición

A modo de ejemplo, el flujo de una petición para crear una nueva tarea sería el siguiente:

1.  Una petición `POST` llega al endpoint `/api/tasks` en la capa de **Infraestructura** (`task_routes.py`).
2.  El controlador de la ruta valida los datos de entrada usando un schema de Pydantic.
3.  El controlador llama al `CreateTaskUseCase` de la capa de **Aplicación**.
4.  El caso de uso utiliza las entidades del **Dominio** para crear una nueva tarea.
5.  El caso de uso utiliza el `TaskGateway` (interfaz del **Dominio**) para guardar la tarea.
6.  La implementación del `TaskRepository` en la capa de **Infraestructura** traduce la entidad del dominio a un modelo de SQLAlchemy y la guarda en la base de datos.
7.  La respuesta viaja de vuelta a través de las capas hasta el cliente.

---

## Próximos Pasos

Para ver un ejemplo práctico de cómo añadir una nueva funcionalidad siguiendo esta arquitectura, consulta la [Guía de Desarrollo](./development-guide.md). 