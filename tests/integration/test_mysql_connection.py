import pytest
from sqlalchemy import text
from infrastructure.driven_adapters.repositories.base import engine

@pytest.mark.asyncio
async def test_mysql_connection():
    """
    Test de integración para verificar la conexión a MySQL y la existencia de tablas
    """
    # Probar conexión básica
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1 as test"))
        row = result.fetchone()
        assert row is not None, "No se obtuvo resultado de SELECT 1"
        assert row[0] == 1, "El resultado de SELECT 1 no es 1"

    # Verificar base de datos actual
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT DATABASE() as db_name"))
        db_name = result.fetchone()[0]
        assert db_name == "accounting", f"La base de datos actual es '{db_name}', se esperaba 'accounting'"

        # Verificar que existan tablas
        result = await conn.execute(text("SHOW TABLES"))
        tables = result.fetchall()
        assert len(tables) > 0, "No se encontraron tablas en la base de datos 'accounting'" 