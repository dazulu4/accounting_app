from fastapi import FastAPI, APIRouter
from infrastructure.entrypoints.http import task_routes
from infrastructure.entrypoints.http import user_routes

app = FastAPI(title="Accounting App Backend")

# Router principal para agrupar todas las rutas de la API
api_router = APIRouter()

api_router.include_router(task_routes.router)
api_router.include_router(user_routes.router)


@api_router.get("/health")
def health_check():
    return {"status": "ok"}


# Incluir el router principal con el prefijo /api
app.include_router(api_router, prefix="/api")
