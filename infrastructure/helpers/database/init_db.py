import asyncio
from infrastructure.driven_adapters.repositories.base import Base, engine
from infrastructure.driven_adapters.repositories.task_repository import TaskModel


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_db())
