
from typing import Dict

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from starlette import status

from src.event.models import Event, City
from src.event.shemas.event_schemas import ReadEvent
from tests.conftest import async_session_maker
from tests.fixtures.user_fixtures import user_1, user_2, user_1_auth_header, user_2_auth_header
from tests.fixtures.events_fixture import event_1, city, create_30_events, create_11_cities


@pytest.fixture
async def create_event_data():
    return {
        "city_id": 1,
        "description": "Бег",
        "event_type": "running",
        "location": "POINT(55.676371 37.671569)"
    }


class TestEvents:

    async def test_get_events(self, ac: AsyncClient, create_30_events):
        """Для этого теста нужно отключить кэш на events"""
        DEFAULT_CITY_ID = 1
        res = await ac.get("events/")
        assert res.status_code == 200, "Проверьте, что ендпоинт 'events/' доступен"
        for i in res.json():
            assert i.get("city_id") == DEFAULT_CITY_ID, "Проверьте, что по умолчанию выдаются ивенты города с id 1"

    async def test_city_id_event(self, ac: AsyncClient):
        """Проверка, того, что параметр city_id выдает соответсвующие ивенты"""

        CITY_ID_5 = 5
        res = await ac.get("events/?city_id=5")
        ans = res.json()

        for i in ans:
            assert i.get("city_id") == CITY_ID_5, (
                "Проверьте, что при парвметре city_id"
                "возвращаются события только с этим city_id"
                 )

    async def test_user_send_correct_city_id(self, ac: AsyncClient, user_2_auth_header):
        """
        Проверка, того, что авторизированый юзер отправляет свой city_id
        в параметры запроса 'events/' и получает соответсвующий результат
        """
        USER_2_CITY_ID = 7  # Город user2
        res = await ac.get("events/", headers={**user_2_auth_header})
        ans = res.json()
        for i in ans:
            assert i.get("city_id") == USER_2_CITY_ID, (
                "Проверьте, что при парвметре city_id"
                "возвращаются события только с этим city_id"
                 )

    async def test_get_event(self, event_1: Event, ac: AsyncClient):
        res = await ac.get(f"events/{event_1.id}")
        assert event_1.description == "Бегать"
        assert res.status_code == status.HTTP_200_OK

    async def test_create_event(self, event_1, create_event_data, user_1_auth_header, ac: AsyncClient):
        EXPECTED_DIFFERENCE = 1
        async with async_session_maker() as session:
            count_before_create = await session.execute(func.count(Event.id))
        res = await ac.post(
            f"events/",
            headers={**user_1_auth_header},
            json={
                **create_event_data
            })
        assert res.status_code == status.HTTP_201_CREATED
        async with async_session_maker() as session:
            current_count = await session.execute(func.count(Event.id))
        assert current_count.scalar() - count_before_create.scalar() == EXPECTED_DIFFERENCE, (
            "Проверьте, что элемент создается в базе данных"
        )

    async def test_create_even_by_anon(self, event_1, create_event_data, ac: AsyncClient):
        async with async_session_maker() as session:
            current_before_create = await session.execute(func.count(Event.id))
        res = await ac.post(
            f"events/",
            json={
               **create_event_data
            })
        assert res.status_code == status.HTTP_401_UNAUTHORIZED, (
            "Проверьте, что анонимы не могут создлавать события"
        )
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
            after = await session.scalar(select(Event).where(Event.id == int(event_1.id)))
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
            after = await session.scalar(select(Event).where(Event.id == int(event_1.id)))
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
            removed_event = await session.scalar(select(Event).where(Event.id == int(event_1.id)))
        assert removed_event

    async def test_delete_event_by_anon(self, event_1: Event, ac: AsyncClient):
        res = await ac.delete(
            f"events/{event_1.id}",
        )
        assert res.status_code == 401
        async with async_session_maker() as session:
            removed_event = await session.scalar(select(Event).where(Event.id == int(event_1.id)))
        assert removed_event


    async def test_event_has_correct_city_nam(self, ac: AsyncClient, event_1):
        """Проверка правильности названия города"""
        res = await ac.get(f"events/{event_1.id}")
        async with async_session_maker() as session:
            city_title = await session.scalar(select(City.title).where(City.id == event_1.city_id))
        assert res.json().get("city") == city_title

    async def test_events_has_user_city(
            self, user_1, user_1_auth_header: Dict, ac: AsyncClient, create_30_events):
        """Проверка того, что авторизонный пользователь получает ивенты своего города"""
        res = await ac.get("events/", headers=user_1_auth_header)
        events = res.json()
        for i in events:
            if i.get("city_id") != user_1.get("city_id"):
                assert False , ("Проверьте, что пользователь получает события из своего города")

    async def test_city_selection(self, ac: AsyncClient, create_30_events):
        SOME_CITY_ID = 3
        res = await ac.get(f"events/?city_id={SOME_CITY_ID}")
        events = res.json()
        for event in events:
            if event.get("city_id") != SOME_CITY_ID:
                 assert False , ("Проверьте правильность выьорки событий по городоам ")

    async def test_delete_event_by_owner(self, event_1: Event, user_1_auth_header, ac: AsyncClient):
        res = await ac.delete(
            f"events/{event_1.id}",
            headers={**user_1_auth_header}
        )
        assert res.status_code == 200

        async with async_session_maker() as session:
            removed_event = await session.scalar(select(Event).where(Event.id == int(event_1.id)))
        assert not removed_event