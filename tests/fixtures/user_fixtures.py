from typing import Dict

import pytest
from httpx import AsyncClient
from sqlalchemy import select, insert, update, text

from src.event.models import User
from tests.conftest import async_session_maker
from tests.fixtures.events_fixture import create_11_cities


user_1_register_data =  {
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

user_2_register_data = {
        'email': 'user2@gmail.com',
        'password': '123',
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "city_id": 1,
        "first_name": "Vasya",
        "last_name": "Vasin",
        "date_of_birth": "2002-09-06"
}


@pytest.fixture
async def user_1(ac: AsyncClient, create_11_cities) -> Dict:
    user_data = {
     **user_1_register_data
    }
    await ac.post('/auth/register', json={
        **user_data
    })
    auth_user = await ac.post('/auth/jwt/login', data={
        'username': user_data.get("email"), "password": user_data.get("password")})

    async with async_session_maker() as session:
        user = await session.scalar(select(User).where(User.email == user_data.get("email")))

    return {
        "Authorization": f'bearer {auth_user.json().get("access_token")}',
        "id": user.id,
        "first_name": user.first_name,
        "city_id": user.city_id
    }



@pytest.fixture
async def user_2(ac: AsyncClient):
    user_data = {
        **user_2_register_data
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
        user = await session.scalar(select(User).where(User.email == user_data.get("email")))

    return {
        "Authorization": f'bearer {auth_user.json().get("access_token")}',
        "id": user.id,
        "first_name": user.first_name
    }


@pytest.fixture
async def user_1_auth_header(user_1: Dict):
    token = user_1.get("Authorization")
    return {"Authorization": token}


@pytest.fixture
async def user_2_auth_header(user_2: Dict):
    token = user_2.get("Authorization")
    return {"Authorization": token}



