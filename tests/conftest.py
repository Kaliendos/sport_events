import asyncio
import os

from typing import AsyncGenerator

import dotenv
import pytest
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.core.database import Base, get_async_session
from src.main import app

load_dotenv()


DB_USER = os.environ.get("DB_USER_TEST")
DB_PASSWORD = os.environ.get("DB_PASS_TEST")
DB_HOST = os.environ.get("DB_HOST_TEST")
DB_PORT = os.environ.get("DB_PORT_TEST")
SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/tests"
print("====================================>",DB_PASSWORD, DB_USER, DB_HOST, DB_PORT,"<<<<=================================================================")

test_engine = create_async_engine(SQLALCHEMY_DATABASE_URL)


async_session_maker = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


Base.bind = test_engine


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session



@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


client = TestClient(app)



@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
