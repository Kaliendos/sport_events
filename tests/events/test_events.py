from typing import Dict

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select

from src.event.models import Event
from src.event.shemas.event_schemas import ReadEvent
from tests.conftest import async_session_maker
from tests.fixtures.user_fixtures import user_1, user_2
from tests.fixtures.events_fixture import event_1, city
import sqlalchemy as sa


def test_a():
    assert 10 > 1

@pytest.fixture
async def user_1_auth_header(user_1: Dict):
    token = user_1.get("Authorization")
    return {"Authorization": token}


@pytest.fixture
async def user_2_auth_header(user_2: Dict):
    token = user_2.get("Authorization")
    return {"Authorization": token}

@pytest.fixture
async def create_event_data():
    return {
        "city_id": 1,
        "description": "Бегать",
        "event_type": "running",
        "location": "POINT(55.676371 37.671569)"
    }


class TestEvents:

    async def test_get_events(self, user_1, ac: AsyncClient):
        res = await ac.get("events/")
        assert res.status_code == 200

    async def test_get_event(self, event_1: Event, ac: AsyncClient):
        res = await ac.get(f"events/{event_1.id}")
        assert event_1.description == "Бегать"
        assert res.status_code == 200

    async def test_create_event(self, event_1, create_event_data, user_1_auth_header, ac: AsyncClient):
        async with async_session_maker() as session:
            count_before_create = await session.execute(func.count(Event.id))
        res = await ac.post(
            f"events/",
            headers={**user_1_auth_header},
            json={
                **create_event_data
            })
        assert res.status_code == 201
        async with async_session_maker() as session:
            current_count = await session.execute(func.count(Event.id))
        assert current_count.scalar() - count_before_create.scalar() == 1

    async def test_create_even_by_anon(self, event_1, create_event_data, ac: AsyncClient):
        async with async_session_maker() as session:
            current_before_create = await session.execute(func.count(Event.id))
        res = await ac.post(
            f"events/",
            json={
               **create_event_data
            })
        assert res.status_code == 401, "Проверьте, что анонимы не могут создлавать события"
        async with async_session_maker() as session:
            current_count = await session.execute(func.count(Event.id))
        assert current_count.scalar() - current_before_create.scalar() == 0

    async def test_patch_event_by_owner(self, event_1: Event, user_1_auth_header, ac: AsyncClient):
        event_before = event_1
        res = await ac.patch(
            url=f"events/{event_1.id}",
            headers={**user_1_auth_header},
            json={"description": "nice"}
        )
        assert res.status_code == 200, "Проверьте, чо пользователь может изменять свои события"
        async with async_session_maker() as session:
            after = await session.scalar(select(Event).where(Event.id == event_1.id))
        assert event_before.description != after.description

    async def test_path_event_by_another_user(self, event_1: Event, user_2_auth_header, ac: AsyncClient):
        event_before = event_1
        res = await ac.patch(
            url=f"events/{event_1.id}",
            headers={**user_2_auth_header},
            json={"description": "nice"}
        )
        assert res.status_code == 403, (
            "Проверьте, что пользователь не может изменять чужие события",
            "Возможно, следует проверить object_permission"
            )
        async with async_session_maker() as session:
            after = await session.scalar(select(Event).where(Event.id == event_1.id))
        assert event_before.description == after.description

    async def test_path_event_by_anon(self, event_1: Event, ac: AsyncClient):
        event_before = event_1
        res = await ac.patch(
            url=f"events/{event_1.id}",
            json={"description": "nice"}
        )
        assert res.status_code == 401, (
            "Проверьте, что анониму при попытке удаления события возвращается 401"
        )
        async with async_session_maker() as session:
            after = await session.scalar(select(Event).where(Event.id == event_1.id))
        assert event_before.description == after.description

    async def test_delete_event_by_another(self, event_1: Event, user_2_auth_header, ac: AsyncClient):
        res = await ac.delete(
                f"events/{event_1.id}",
                headers={**user_2_auth_header}
        )

        assert res.status_code == 403
        async with async_session_maker() as session:
            removed_event = await session.scalar(select(Event).where(Event.id == event_1.id))
        assert removed_event

    async def test_delete_event_by_anon(self, event_1: Event, ac: AsyncClient):
        res = await ac.delete(
            f"events/{event_1.id}",
        )

        assert res.status_code == 401
        async with async_session_maker() as session:
            removed_event = await session.scalar(select(Event).where(Event.id == event_1.id))
        assert removed_event

    async def test_delete_event_by_owner(self, event_1: Event, user_1_auth_header, ac: AsyncClient):
        res = await ac.delete(
            f"events/{event_1.id}",
            headers={**user_1_auth_header}
        )

        assert res.status_code == 200

        async with async_session_maker() as session:
            removed_event = await session.scalar(select(Event).where(Event.id == event_1.id))
        assert not removed_event





