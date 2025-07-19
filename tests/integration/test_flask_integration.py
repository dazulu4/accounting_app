"""
Pruebas de integración para validar la migración de FastAPI a Flask

Estas pruebas validan:
- Que la aplicación Flask se inicie correctamente
- Que las rutas respondan como se espera
- Que la funcionalidad básica esté operativa
- Que el manejo de errores funcione correctamente
"""

import pytest
import requests
import time
from typing import Dict, Any


class TestFlaskMigration:
    """Pruebas de integración para la migración a Flask"""
    
    @pytest.fixture
    def base_url(self):
        """URL base para las pruebas"""
        return "http://localhost:8000"
    
    @pytest.fixture
    def wait_for_server(self):
        """Esperar a que el servidor esté listo"""
        time.sleep(2)
    
    def test_health_endpoint(self, base_url, wait_for_server):
        """Prueba el endpoint de health check"""
        response = requests.get(f"{base_url}/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
    
    def test_list_users(self, base_url, wait_for_server):
        """Prueba el endpoint de listar usuarios"""
        response = requests.get(f"{base_url}/api/users")
        
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) > 0
    
    def test_create_task(self, base_url, wait_for_server):
        """Prueba el endpoint de crear tarea"""
        task_data = {
            "title": "Tarea de prueba Flask",
            "description": "Descripción de prueba para validar migración",
            "user_id": 1
        }
        
        response = requests.post(
            f"{base_url}/api/tasks",
            json=task_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 201
        task = response.json()
        assert task.get("title") == task_data["title"]
        assert task.get("description") == task_data["description"]
        assert task.get("user_id") == task_data["user_id"]
        assert "task_id" in task
        assert "created_at" in task
        
        return task.get("task_id")
    
    def test_list_tasks(self, base_url, wait_for_server):
        """Prueba el endpoint de listar tareas"""
        response = requests.get(f"{base_url}/api/tasks/1")
        
        assert response.status_code == 200
        tasks = response.json()
        assert isinstance(tasks, list)
    
    def test_complete_task(self, base_url, wait_for_server):
        """Prueba el endpoint de completar tarea"""
        # Primero crear una tarea
        task_data = {
            "title": "Tarea para completar",
            "description": "Tarea que será completada",
            "user_id": 1
        }
        
        create_response = requests.post(
            f"{base_url}/api/tasks",
            json=task_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert create_response.status_code == 201
        task_id = create_response.json().get("task_id")
        
        # Ahora completar la tarea
        complete_response = requests.put(f"{base_url}/api/tasks/{task_id}/complete")
        
        assert complete_response.status_code == 200
        message = complete_response.json()
        assert "message" in message
        assert "completada" in message["message"]
    
    def test_invalid_data_handling(self, base_url, wait_for_server):
        """Prueba el manejo de datos inválidos"""
        # Datos inválidos
        invalid_data = {
            "title": "",  # Título vacío
            "description": "Descripción válida",
            "user_id": 0  # user_id inválido
        }
        
        response = requests.post(
            f"{base_url}/api/tasks",
            json=invalid_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400
        error = response.json()
        assert "error" in error
    
    def test_invalid_user_id(self, base_url, wait_for_server):
        """Prueba crear tarea con usuario inexistente"""
        task_data = {
            "title": "Tarea con usuario inexistente",
            "description": "Descripción de prueba",
            "user_id": 999  # Usuario que no existe
        }
        
        response = requests.post(
            f"{base_url}/api/tasks",
            json=task_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400
        error = response.json()
        assert "error" in error
    
    def test_complete_nonexistent_task(self, base_url, wait_for_server):
        """Prueba completar una tarea que no existe"""
        import uuid
        
        fake_task_id = str(uuid.uuid4())
        response = requests.put(f"{base_url}/api/tasks/{fake_task_id}/complete")
        
        assert response.status_code == 404
        error = response.json()
        assert "error" in error
    
    def test_api_endpoints_structure(self, base_url, wait_for_server):
        """Prueba que todos los endpoints principales estén disponibles"""
        endpoints = [
            ("/api/health", "GET"),
            ("/api/users", "GET"),
            ("/api/tasks/1", "GET"),
        ]
        
        for endpoint, method in endpoints:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}")
                assert response.status_code in [200, 404]  # 404 es válido para tareas inexistentes
    
    def test_cors_headers(self, base_url, wait_for_server):
        """Prueba que los headers CORS estén configurados"""
        response = requests.get(f"{base_url}/api/health")
        
        # Verificar que la respuesta no falle por CORS
        assert response.status_code == 200
        
        # Verificar headers CORS si están presentes
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods",
            "Access-Control-Allow-Headers"
        ]
        
        # Al menos uno de los headers CORS debe estar presente
        present_cors_headers = [h for h in cors_headers if h in response.headers]
        assert len(present_cors_headers) > 0
    
    def test_error_handlers(self, base_url, wait_for_server):
        """Prueba que los manejadores de error funcionen"""
        # Probar endpoint inexistente
        response = requests.get(f"{base_url}/api/nonexistent")
        assert response.status_code == 404
        
        # Probar método no permitido
        response = requests.post(f"{base_url}/api/health")
        assert response.status_code == 405  # Method Not Allowed


class TestFlaskMigrationEndToEnd:
    """Pruebas end-to-end para validar flujos completos"""
    
    @pytest.fixture
    def base_url(self):
        """URL base para las pruebas"""
        return "http://localhost:8000"
    
    @pytest.fixture
    def wait_for_server(self):
        """Esperar a que el servidor esté listo"""
        time.sleep(2)
    
    def test_complete_task_workflow(self, base_url, wait_for_server):
        """Prueba el flujo completo: crear -> listar -> completar tarea"""
        # 1. Crear tarea
        task_data = {
            "title": "Tarea de flujo completo",
            "description": "Prueba del flujo completo de tareas",
            "user_id": 1
        }
        
        create_response = requests.post(
            f"{base_url}/api/tasks",
            json=task_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert create_response.status_code == 201
        created_task = create_response.json()
        task_id = created_task.get("task_id")
        
        # 2. Verificar que aparece en la lista
        list_response = requests.get(f"{base_url}/api/tasks/1")
        assert list_response.status_code == 200
        tasks = list_response.json()
        
        # Buscar la tarea creada en la lista
        found_task = None
        for task in tasks:
            if task.get("task_id") == task_id:
                found_task = task
                break
        
        assert found_task is not None
        assert found_task.get("title") == task_data["title"]
        
        # 3. Completar la tarea
        complete_response = requests.put(f"{base_url}/api/tasks/{task_id}/complete")
        assert complete_response.status_code == 200
        
        # 4. Verificar que se completó correctamente
        complete_message = complete_response.json()
        assert "completada" in complete_message.get("message", "")
    
    def test_multiple_tasks_workflow(self, base_url, wait_for_server):
        """Prueba crear múltiples tareas y verificar el listado"""
        # Crear varias tareas
        task_titles = [
            "Tarea 1 del flujo múltiple",
            "Tarea 2 del flujo múltiple",
            "Tarea 3 del flujo múltiple"
        ]
        
        created_tasks = []
        
        for title in task_titles:
            task_data = {
                "title": title,
                "description": f"Descripción de {title}",
                "user_id": 1
            }
            
            response = requests.post(
                f"{base_url}/api/tasks",
                json=task_data,
                headers={"Content-Type": "application/json"}
            )
            
            assert response.status_code == 201
            created_tasks.append(response.json())
        
        # Verificar que todas aparecen en el listado
        list_response = requests.get(f"{base_url}/api/tasks/1")
        assert list_response.status_code == 200
        all_tasks = list_response.json()
        
        # Verificar que al menos las tareas creadas están en la lista
        created_titles = {task.get("title") for task in created_tasks}
        list_titles = {task.get("title") for task in all_tasks}
        
        # Al menos una de las tareas creadas debe estar en la lista
        assert len(created_titles.intersection(list_titles)) > 0 