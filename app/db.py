from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .config import settings
from contextlib import asynccontextmanager

# Создание асинхронного движка для подключения к базе данных
DATABASE_URL = settings.db.url
engine = create_async_engine(DATABASE_URL, echo=settings.db.echo, future=True)

# Создание фабрики асинхронных сессий (sessionmaker)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Вспомогательная функция для получения асинхронной сессии БД
# Используется как зависимость в FastAPI эндпоинтах
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
