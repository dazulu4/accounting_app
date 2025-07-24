# Guía de Desarrollo: Cómo Añadir una Nueva Funcionalidad

Esta guía proporciona un ejemplo práctico y paso a paso sobre cómo añadir una nueva funcionalidad al sistema, respetando los principios de **Clean Architecture**.

**Objetivo del Ejemplo**: Vamos a crear una funcionalidad para gestionar "Notas Contables" (`AccountingNote`). Una nota tendrá un ID, contenido y una fecha.

---

## Paso 1: Definir la Entidad en la Capa de Dominio

Primero, definimos la entidad de negocio en el corazón de nuestra aplicación.

1.  **Crear el archivo de la entidad**: `domain/entities/accounting_note_entity.py`

2.  **Definir la clase `AccountingNote`**:

    ```python
    # domain/entities/accounting_note_entity.py
    import uuid
    from datetime import datetime
    from pydantic import BaseModel, Field

    class AccountingNote(BaseModel):
        id: uuid.UUID = Field(default_factory=uuid.uuid4)
        content: str
        created_at: datetime = Field(default_factory=datetime.utcnow)

        def update_content(self, new_content: str):
            """Actualiza el contenido de la nota."""
            self.content = new_content
    ```

---

## Paso 2: Definir el Gateway en la Capa de Dominio

Ahora, definimos la interfaz que la aplicación usará para interactuar con la persistencia de las notas.

1.  **Crear el archivo del gateway**: `domain/gateways/accounting_note_gateway.py`

2.  **Definir la interfaz `AccountingNoteGateway`**:

    ```python
    # domain/gateways/accounting_note_gateway.py
    from abc import ABC, abstractmethod
    import uuid
    from typing import Optional
    from domain.entities.accounting_note_entity import AccountingNote

    class AccountingNoteGateway(ABC):
        @abstractmethod
        def save(self, note: AccountingNote) -> AccountingNote:
            """Guarda una nota contable."""
            raise NotImplementedError

        @abstractmethod
        def find_by_id(self, note_id: uuid.UUID) -> Optional[AccountingNote]:
            """Encuentra una nota por su ID."""
            raise NotImplementedError
    ```

---

## Paso 3: Crear el Caso de Uso en la Capa de Dominio

El caso de uso orquesta la lógica de negocio para crear una nueva nota.

1.  **Crear el archivo del caso de uso**: `domain/usecases/create_accounting_note_use_case.py`

2.  **Definir la clase `CreateAccountingNoteUseCase`**:

    ```python
    # domain/usecases/create_accounting_note_use_case.py
    from domain.entities.accounting_note_entity import AccountingNote
    from domain.gateways.accounting_note_gateway import AccountingNoteGateway

    class CreateAccountingNoteUseCase:
        def __init__(self, accounting_note_gateway: AccountingNoteGateway):
            self.accounting_note_gateway = accounting_note_gateway

        def execute(self, content: str) -> AccountingNote:
            new_note = AccountingNote(content=content)
            return self.accounting_note_gateway.save(new_note)
    ```

---

## Paso 4: Implementar el Repositorio en la Capa de Infraestructura

Ahora, creamos la implementación concreta del gateway, que interactuará con la base de datos.

1.  **Crear el archivo del repositorio**: `infrastructure/driven_adapters/repositories/accounting_note_repository.py`

2.  **Implementar `AccountingNoteGateway`**:

    ```python
    # infrastructure/driven_adapters/repositories/accounting_note_repository.py
    # (Esta es una implementación de ejemplo en memoria)

    import uuid
    from typing import Dict, Optional
    from domain.entities.accounting_note_entity import AccountingNote
    from domain.gateways.accounting_note_gateway import AccountingNoteGateway

    class InMemoryAccountingNoteRepository(AccountingNoteGateway):
        def __init__(self):
            self._notes: Dict[uuid.UUID, AccountingNote] = {}

        def save(self, note: AccountingNote) -> AccountingNote:
            self._notes[note.id] = note
            return note

        def find_by_id(self, note_id: uuid.UUID) -> Optional[AccountingNote]:
            return self._notes.get(note_id)
    ```
    *Nota: Una implementación real usaría SQLAlchemy para interactuar con MySQL.*

---

## Paso 5: Añadir el Endpoint en la Capa de Infraestructura

Finalmente, exponemos la funcionalidad a través de una API REST.

1.  **Crear el archivo de rutas**: `infrastructure/entrypoints/http/accounting_note_routes.py`

2.  **Definir la ruta de Flask**:

    ```python
    # infrastructure/entrypoints/http/accounting_note_routes.py
    from flask import Blueprint, request, jsonify
    from application.container import container

    # Asume que el caso de uso está registrado en el contenedor de dependencias
    create_note_use_case = container.create_accounting_note_use_case()

    accounting_note_bp = Blueprint('accounting_note_bp', __name__)

    @accounting_note_bp.route('/api/notes', methods=['POST'])
    def create_note():
        data = request.get_json()
        content = data.get('content')
        
        if not content:
            return jsonify({"error": "Content is required"}), 400

        new_note = create_note_use_case.execute(content=content)
        
        return jsonify(new_note.dict()), 201
    ```

---

## Resumen del Proceso

1.  **Dominio**: Define `Qué` hace el sistema (Entidades, Gateways, Casos de Uso).
2.  **Infraestructura**: Implementa `Cómo` lo hace (Repositorios, Controladores).
3.  **Flujo**: La petición entra por la Infraestructura, es manejada por un Caso de Uso, que utiliza abstracciones del Dominio, y la Infraestructura se encarga de los detalles de persistencia.

Siguiendo estos pasos, te aseguras de que la lógica de negocio permanezca limpia y desacoplada de los detalles de implementación. 