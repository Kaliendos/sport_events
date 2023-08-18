import datetime
import random
import string

import pytest
from httpx import AsyncClient
import sqlalchemy as sa
from sqlalchemy import select

from src.event.shemas.event_schemas import ReadEvent
from src.event.models import City, Event
from tests.conftest import async_session_maker

@pytest.fixture
async def create_11_cities():

    cities_name = (
        "Санкт Петербург", "Калининград", "Казань", "Нижний Новгород", "Новосибирск",
        "Тула", "Тверь", "Владивосток", "Сочи", "Ростов", "Краснодар"
    )
    for city in cities_name:
        async with async_session_maker() as session:
            await session.execute(sa.insert(City).values(
                title=city
            ))
            await session.commit()


async def create_city(title):
    async with async_session_maker() as session:
        await session.execute(sa.insert(City).values(title=title))
        await session.commit()
        return await session.scalar(sa.select(City))


@pytest.fixture
async def city():
    return await create_city("Moscow")


@pytest.fixture
async def city2():
    return await create_city("SPB")




@pytest.fixture
async def event_1(city, ac: AsyncClient, user_1):

    async with async_session_maker() as session:
        await session.execute(sa.insert(Event).values(
            city_id=1,
            description='Бегать',
            event_type='running',
            datetime=datetime.datetime.now(),
            location='POINT(55.676371 37.671569)',
            owner_id=user_1.get("id")

        ))
        await session.commit()
        return await session.scalar(sa.select(Event).where(Event.id == 1))


@pytest.fixture
async def event_2(city2, ac: AsyncClient, user_2):

    async with async_session_maker() as session:
        await session.execute(sa.insert(Event).values(
            city_id=2,
            description='Бег',
            event_type='running',
            datetime=datetime.datetime.now(),
            location='POINT(55.676371 37.671569)',
            owner_id=user_2.get("id")

        ))
        await session.commit()
        return await session.scalar(sa.select(Event).where(Event.id == 2))






@pytest.fixture
async def create_100_events(user_1):
    for i in range(10):
        letters = string.ascii_lowercase
        rand_string = ''.join(random.choice(letters) for i in range(20))
        async with async_session_maker() as session:
            await session.execute(sa.insert(Event).values(
                city_id=random.randrange(1,10),
                description=rand_string,
                event_type='running',
                datetime=datetime.datetime.now(),
                location='POINT(55.676371 37.671569)',
                owner_id=user_1.get("id")

            ))
            await session.commit()


