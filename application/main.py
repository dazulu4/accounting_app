"""
Punto de entrada principal de la aplicación usando Flask

¿Qué cambia con Flask?
- Flask es más ligero y flexible que FastAPI
- Usa Blueprint para organizar rutas (similar a APIRouter)
- Manejo manual de JSON y validaciones
- Mejor compatibilidad con AWS Lambda
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from infrastructure.entrypoints.http import task_routes, user_routes
from application.config import settings

# Crear aplicación Flask
app = Flask(__name__)

# Configurar CORS
CORS(app, 
     origins=settings.api.cors_origins,
     methods=settings.api.cors_methods,
     allow_headers=settings.api.cors_headers)

# Registrar blueprints (equivalente a APIRouter en FastAPI)
app.register_blueprint(task_routes.blueprint, url_prefix='/api/tasks')
app.register_blueprint(user_routes.blueprint, url_prefix='/api/users')

# Health check endpoint
@app.route('/api/health')
def health_check():
    """Endpoint de health check"""
    return jsonify({"status": "ok"})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Manejar errores 404"""
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Manejar errores 500"""
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(400)
def bad_request(error):
    """Manejar errores 400"""
    return jsonify({"error": "Bad request"}), 400

if __name__ == '__main__':
    # Ejecutar en modo desarrollo
    app.run(
        host=settings.api.api_host,
        port=settings.api.api_port,
        debug=settings.api.api_debug
    )
