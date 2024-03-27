from typing import Dict
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy import insert, select, func
from starlette import status

from src.event.models import Comment, Event
from tests.conftest import async_session_maker
from tests.fixtures.events_fixture import event_1, city, event_2, create_11_cities
from tests.fixtures.user_fixtures import user_2, user_1_register_data, user_1_auth_header, user_2_auth_header, user_1


async def test_create_like(event_1: Event, user_1_auth_header: Dict, ac: AsyncClient):
    get_event = await ac.get(f"events/{event_1.id}")
    going_users_before = get_event.json().get("going")
    await ac.post(f"events/going/{event_1.id}", headers=user_1_auth_header)
    get_event = await ac.get(f"events/{event_1.id}")
    going_users_after = get_event.json().get("going")
    assert len(going_users_after) - len(going_users_before) == 1, (
        "Проверьте, что пользователь может ставить лайк"
    )


async def test_delete_like(
        event_1: Event, user_1_auth_header: Dict, user_2_auth_header: Dict,
        ac: AsyncClient
):
    await ac.post(f"events/going/{event_1.id}", headers=user_1_auth_header)
    get_event = await ac.get(f"events/{event_1.id}")
    going_users_before = get_event.json().get("going")
    await ac.delete(f"events/going/{event_1.id}", headers=user_1_auth_header)
    get_event = await ac.get(f"events/{event_1.id}")
    going_users_after = get_event.json().get("going")
    assert len(going_users_after) == len(going_users_before) -1


async def test_like_dont_delete_by_other(
        event_1: Event, user_1_auth_header: Dict, user_2_auth_header: Dict,
        ac: AsyncClient
):
    await ac.post(f"events/going/{event_1.id}", headers=user_1_auth_header)
    get_event = await ac.get(f"events/{event_1.id}")
    going_users_before = get_event.json().get("going")
    await ac.delete(f"events/going/{event_1.id}", headers=user_2_auth_header)
    get_event = await ac.get(f"events/{event_1.id}")
    going_users_after = get_event.json().get("going")
    assert len(going_users_after) != len(going_users_before) -1

