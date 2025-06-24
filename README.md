# Accounting App Backend

Backend Python basado en Clean Architecture usando FastAPI.

## 🚀 Requisitos

- Python 3.11 o superior (funciona con 3.13.x)
- [Poetry](https://python-poetry.org/docs/#installation)
- Git

## ⚙️ Instalación local

```bash
# Clonar el repositorio
git clone https://github.com/tuusuario/accounting_app.git
cd accounting_app

# Instalar dependencias
poetry install
```

## 🚀 Ejecutar el servidor

**Opción recomendada (más confiable):**
```bash
poetry run uvicorn application.main:app --reload
```

**Opción alternativa (puede tener problemas con rutas largas):**
```bash
# Activar entorno virtual
poetry env activate

# Ejecutar servidor
uvicorn application.main:app --reload
```

> **Nota**: Se recomienda usar `poetry run` ya que evita problemas con rutas largas de Windows y es más confiable en diferentes entornos.

## 🧰 Configuración de Base de Datos (SQLite + SQLAlchemy)
Esta aplicación utiliza SQLAlchemy 2.x en modo async con SQLite como motor local de base de datos.

### 📦 Requisitos
```
poetry add sqlalchemy --extras asyncio
poetry add aiosqlite
```

### 🛠 Inicializar la base de datos
```
poetry run python infrastructure/helpers/database/init_db.py
```
Se creará el archivo accounting.db con la tabla tasks.
> En producción puede sustituirse fácilmente por MySQL o PostgreSQL ajustando DATABASE_URL en `base.py`.

## 📡 Ejemplos de Endpoints

### Crear una nueva tarea
**Endpoint:** `POST http://127.0.0.1:8000/api/tasks`

**Descripción:** Crea una nueva tarea contable con título, descripción y usuario asignado.

**Body JSON:**
```json
{
  "title": "Revisión contable mensual",
  "description": "Auditoría y conciliación de cuentas",
  "user_id": 1
}
```

**Respuesta esperada:**
```json
{
  "task_id": "GENERATED_UUID",
  "title": "Revisión contable mensual",
  "description": "Auditoría y conciliación de cuentas",
  "status": "NEW",
  "created_at": "2025-06-23T01:23:45.000Z"
}
```

> **Nota:** Si usas un `user_id` que no existe, recibirás un error 400 con el mensaje: "Usuario no existe o está inactivo"

### Listar tareas de un usuario
**Endpoint:** `GET http://127.0.0.1:8000/api/tasks/{user_id}`

**Descripción:** Obtiene todas las tareas asociadas a un usuario específico.

**Ejemplo:**
```bash
GET http://127.0.0.1:8000/api/tasks/1
```

### Listar todos los usuarios activos
**Endpoint:** `GET http://127.0.0.1:8000/api/users`

**Descripción:** Obtiene la lista de todos los usuarios activos en el sistema.

### Completar una tarea
**Endpoint:** `PUT http://127.0.0.1:8000/api/tasks/{task_id}/complete`

**Descripción:** Marca una tarea como completada y actualiza su timestamp de finalización.

**Ejemplo:**
```bash
PUT http://127.0.0.1:8000/api/tasks/<TASK_ID>/complete
```

> **Nota:** Este endpoint emite un evento informando que la tarea fue completada. La salida en consola será algo como: `[EVENT] TaskCompleted: task_id=..., user_id=...`

### Simular evento externo (inactivar usuario)
**Endpoint:** `POST http://127.0.0.1:8000/api/users/{user_id}/deactivate`

**Descripción:** Simula la inactivación de un usuario mediante un evento externo.

**Ejemplo:**
```bash
POST http://127.0.0.1:8000/api/users/1/deactivate
```

> **Nota:** La salida en consola será: `[EVENT RECEIVED] Usuario 1 inactivado`

## 📋 Resumen de Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/users` | Lista todos los usuarios activos |
| GET | `/api/tasks/{user_id}` | Lista las tareas de un usuario |
| POST | `/api/tasks` | Crea una nueva tarea |
| PUT | `/api/tasks/{task_id}/complete` | Completa una tarea existente |
| POST | `/api/users/{user_id}/deactivate` | Simula inactivación de usuario (evento externo) |

## 🧱 Estructura del Proyecto (Clean Architecture)

```
accounting_app/
├── application/                # Capa de orquestación e inicio
│   ├── main.py                 # FastAPI app principal
│   └── di_container.py         # Inyección de dependencias
├── domain/                     # Capa de dominio puro (negocio)
│   ├── models/                 # Entidades de dominio (User, Task)
│   ├── gateways/               # Interfaces (UserGateway, TaskGateway)
│   └── usecases/               # Casos de uso (Create, Complete, etc.)
├── infrastructure/             # Adaptadores externos y persistencia
│   ├── driven_adapters/
│   │   ├── repositories/       # Repositorios SQLAlchemy async
│   │   ├── event_sender/       # Emisión de eventos (simulado)
│   │   └── event_receiver/     # Recepción de eventos (simulado)
│   ├── entrypoints/
│   │   └── http/               # Rutas FastAPI (tasks, users)
│   └── helpers/                # Init DB, logging, utilidades
├── tests/                      # Pruebas unitarias
├── pyproject.toml              # Configuración de dependencias con Poetry
└── README.md                   # Documentación principal
```

## 🚀 Comandos Rápidos para Desarrollo

Usa `make` en Linux/macOS:

```bash
make run        # Inicia el servidor FastAPI en modo desarrollo
make db-init    # Inicializa la base de datos SQLite
make test       # Ejecuta pruebas unitarias
```

O si usas Windows (sin make), ejecuta:

```cmd
make.bat run
make.bat db-init
make.bat test
```

## ✅ Ejecutar Pruebas

Para correr los tests unitarios:

```bash
make test
```

Esto ejecuta las pruebas ubicadas en la carpeta `tests/`.

Por ejemplo:

- `test_task_creation_defaults`: valida que una tarea nueva tenga estado `NEW`
- `test_task_completion_sets_status`: verifica que al completar una tarea cambie a `COMPLETED` y registre `completed_at`

## 🎁 Resultado Final

Con esta base, el backend está listo para desarrollo colaborativo, integración con frontend Angular, y despliegue en ambiente de pruebas.

### ✅ Características actuales

- 🧱 Arquitectura Clean Architecture desacoplada y mantenible
- ⚡️ Backend en FastAPI + SQLAlchemy async + SQLite (listo para migrar a MySQL)
- 📁 Separación clara en módulos: application, domain, infrastructure
- 🧪 Tests básicos incluidos
- 🚀 Sistema de comandos rápidos (`make` o `make.bat`)
- 📡 Simulación de eventos de entrada/salida
- 🤝 Preparado para consumir REST externos (como sistema de usuarios)

---

## 🧭 ¿Qué sigue?

### Opción A – Extender Backend (Etapas siguientes)

- 🔐 **Autenticación JWT** y control de acceso
- 📄 **Auditoría** de acciones y eventos
- 💼 Módulo contable real: transacciones, cuentas, balances
- 📤 Notificaciones, envío de correos, logs distribuidos
- 🧩 Comunicación entre microservicios (RabbitMQ, Kafka, etc.)

### Opción B – Iniciar Frontend Angular 19/20

- Conexión a endpoints existentes:
  - `POST /api/tasks`
  - `GET /api/tasks/{user_id}`
  - `PUT /api/tasks/{task_id}/complete`
- Creación de componentes para usuarios, tareas y eventos
- Desarrollo de tablero contable (futuro módulo funcional)

---

## 💡 Recomendaciones

- Usa entornos virtuales aislados con `Poetry`
- Para desarrollo colaborativo: configura `pre-commit` y `black`
- Para entornos reales: añade migraciones (Alembic), logging estructurado y dockerización

---
