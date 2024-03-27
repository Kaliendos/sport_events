import os
from typing import AsyncGenerator



from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import  dotenv
dotenv.load_dotenv()
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASS")
DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")

DB_PORT = os.environ.get("DB_PORT")

SQLALCHEMY_DATABASE_URL = (
 f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"

)
print(SQLALCHEMY_DATABASE_URL)



engine = create_async_engine(SQLALCHEMY_DATABASE_URL)


async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


Base = declarative_base()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
