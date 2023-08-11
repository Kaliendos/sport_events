import datetime

import pytest
from httpx import AsyncClient
import sqlalchemy as sa

from src.event.shemas.event_schemas import ReadEvent
from src.event.models import City, Event
from tests.conftest import async_session_maker


@pytest.fixture
async def city():
    async with async_session_maker() as session:
        await session.execute(sa.insert(City).values(title="Moscow"))
        await session.commit()
        return await session.scalar(sa.select(City))

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


