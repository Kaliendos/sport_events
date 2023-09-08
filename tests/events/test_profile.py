from typing import Dict

from httpx import AsyncClient
from starlette import status
from sqlalchemy import text, select, func
from sqlalchemy.sql.functions import count

from src.event.models import Event
from tests.conftest import async_session_maker
from tests.fixtures.user_fixtures import user_1, user_2, user_1_auth_header, user_2_auth_header
from tests.fixtures.events_fixture import event_1, city, create_30_events, create_11_cities
class TestProfile:
    DEFAULT_PAGINATION_INDEX = 10

    async def test_user_has_correct_pagination_events(
            self, user_1, user_1_auth_header: Dict, ac: AsyncClient, create_30_events):
        res = await ac.get("users/me", headers=user_1_auth_header)
        assert len(res.json().get("events")) == self.DEFAULT_PAGINATION_INDEX, (
            "Проверьте, что ивенты возвращаются по 10"
        )

    async def test_update_user(self, user_1, user_1_auth_header: Dict, ac: AsyncClient):
        response_before_update = await ac.get("users/me", headers=user_1_auth_header)
        city_id_before_update = response_before_update.json().get("city_id")
        res = await ac.patch(
            "users/me", headers=user_1_auth_header, json={"city_id": 7})
        response_after_update = await ac.get("users/me", headers=user_1_auth_header)
        city_id_after_update = response_after_update.json().get("city_id")
        assert res.status_code == 200
        assert city_id_after_update != city_id_before_update

    async def test_update_user_by_another(
            self, user_1, user_2_auth_header: Dict, user_1_auth_header: Dict, ac: AsyncClient):
        res = await ac.patch(
            f"users/{user_1.get('id')}", headers=user_2_auth_header, json={"city_id": 3})
        assert res.status_code == 405

    async def test_delete_user_by_another(
            self, user_1, user_2_auth_header: Dict, user_1_auth_header: Dict, ac: AsyncClient):
        res = await ac.delete(
            f"users/{user_1.get('id')}", headers=user_2_auth_header)
        assert res.status_code == 405

    async def test_users_me_return_correct_profile(
            self, user_1, user_2, user_1_auth_header, user_2_auth_header, ac: AsyncClient):
        response = await ac.get("users/me", headers=user_1_auth_header)
        firstname_user_1 = user_1.get("first_name")
        firstname_user_2 = user_2.get("first_name")
        firstname_from_response = response.json().get("first_name")
        assert firstname_from_response == firstname_user_1

    async def test_users_returns_401_for_anon(
            self, ac: AsyncClient):
        response = await ac.get("users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

