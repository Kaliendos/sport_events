from httpx import AsyncClient
from sqlalchemy import func

from src.event.models import Event
from src.event.shemas.event_schemas import ReadEvent
from tests.conftest import async_session_maker
from tests.fixtures.user_fixtures import user_1, user_2
from tests.fixtures.events_fixture import event_1, city
import sqlalchemy as sa

def test_a():
    assert 10 > 1


async def test_get(user_1, ac: AsyncClient):
    res = await ac.get("http://localhost:8000/")
    assert res.status_code == 200


async def test_event(event_1, ac: AsyncClient):
    res = await ac.get(f"http://localhost:8000/{event_1.id}")
    assert event_1.description == "Бегать"
    assert res.status_code == 200


async def test_post_event(event_1, user_1, ac: AsyncClient):
    async with async_session_maker() as session:
        count1 = await session.execute(func.count(Event.id))
    res = await ac.post(
        f"http://localhost:8000/",
        headers={"Authorization": user_1.get("Authorization")},
        json={
            "city_id": 1,
            "description": "Бегать",
            "event_type": "running",
            "datetime": "2023-07-29 19:30:00",
            "location": "POINT(55.676371 37.671569)"
        })
    assert res.status_code == 200
    async with async_session_maker() as session:
        count = await session.execute(func.count(Event.id))

    assert count.scalar() - count1.scalar() == 1
