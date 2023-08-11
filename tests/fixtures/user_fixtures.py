import pytest
from httpx import AsyncClient
from sqlalchemy import select


from src.event.models import User
from tests.conftest import async_session_maker


@pytest.fixture
async def user_1(ac: AsyncClient):
    user_data = {
        'email': 'user1@gmail.com',
        'password': '123',
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
    }
    await ac.post('/auth/register', json={
        **user_data
    })
    auth_user = await ac.post('/auth/jwt/login', data={
        'username': user_data.get("email"), "password": user_data.get("password")})
    async with async_session_maker() as session:
        user_id = await session.scalar(select(User.id).where(User.email == user_data.get("email")))

    return {
        "Authorization": f'bearer {auth_user.json().get("access_token")}',
        "id": user_id
    }



@pytest.fixture
async def user_2(ac: AsyncClient):
    user_data = {
        'email': 'user2@gmail.com',
        'password': '123',
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
    }
    await ac.post('/auth/register', json={
        **user_data
    })
    auth_user = await ac.post('/auth/jwt/login', data={
        'username': user_data.get("email"), "password": user_data.get("password")})
    return {"Authorization": f'bearer {auth_user.json().get("access_token")}'}




