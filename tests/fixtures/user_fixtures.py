from typing import Dict

import pytest
from httpx import AsyncClient
from sqlalchemy import select, insert, update, text

from src.event.models import User
from tests.conftest import async_session_maker
from tests.fixtures.events_fixture import create_11_cities



@pytest.fixture
async def user_1(ac: AsyncClient) -> Dict:
    user_data = {
        'email': 'user1@gmail.com',
        'password': '123',
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "city_id": 1,
        "first_name": "Vladsialav",
        "last_name": "Kaliendo",
        "date_of_birth": "2002-09-06"
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
async def user_2(ac: AsyncClient, create_11_cities):
    user_data = {
        'email': 'user2@gmail.com',
        'password': '123',
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "city_id": 1,
        "first_name": "Vladsialav",
        "last_name": "Kaliendo",
        "date_of_birth": "2002-09-06"
    }
    await ac.post('/auth/register', json={
        **user_data
    })
    auth_user = await ac.post('/auth/jwt/login', data={
        'username': user_data.get("email"), "password": user_data.get("password")})

    async with async_session_maker() as session:
        sql = text(f"""UPDATE  "user" SET city_id = 7 WHERE email = 'user2@gmail.com';""")
        await session.execute(sql)
        await session.commit()
        user_id = await session.scalar(select(User.id).where(User.email == user_data.get("email")))

    return {
        "Authorization": f'bearer {auth_user.json().get("access_token")}',
        "id": user_id
    }




