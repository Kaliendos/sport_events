from typing import Dict
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy import insert, select, func

from src.event.models import Comment, Event
from tests.conftest import async_session_maker
from tests.events.test_events import user_1, user_1_auth_header, user_2_auth_header
from tests.fixtures.events_fixture import event_1, city, event_2
from tests.fixtures.user_fixtures import user_2


USER_1_USERNAME = "user1@gmail.com"
@pytest.fixture
def create_comment_data():
    return {
        "text": "какой-то текст"
    }


@pytest.fixture
async def comment_1(user_1: Dict, event_1: Event):
    async with async_session_maker() as session:
        await session.execute(
            insert(Comment).values(
                text="текст комменатрия 1",
                owner_id=user_1.get("id"),
                event_id=event_1.id),
        )
        await session.commit()
        return await session.scalar(select(Comment).where(Comment.id == 1))


@pytest.fixture
async def comment_2(user_2: Dict, event_1: Event):
    async with async_session_maker() as session:
        await session.execute(
            insert(Comment).values(
                text="текст комменатрия 2",
                owner_id=user_2.get("id"),
                event_id=event_1.id),
        )
        await session.commit()
        return await session.scalar(select(Comment).where(Comment.id == 2))
    

@pytest.fixture
async def comment_3(user_2: Dict, event_2: Event):
    async with async_session_maker() as session:
        await session.execute(
            insert(Comment).values(
                text="текст комменатрия 2",
                owner_id=user_2.get("id"),
                event_id=event_2.id),
        )
        await session.commit()
        return await session.scalar(select(Comment).where(Comment.id ==3 ))


@pytest.fixture
def comments_to_event_1(comment_1, comment_2):
    return comment_1, comment_2


class TestComments:
    async def test_get_events_comments(self, comments_to_event_1, event_1: Event, ac: AsyncClient):
        """Проверяем, что комменатрии создались к нужному событию"""
        res = await ac.get(f"events/{event_1.id}")
        assert len(res.json().get("comments")) == 2

    async def test_create_comment(self, create_comment_data, event_1: Event, user_1_auth_header, ac: AsyncClient):
        async with async_session_maker() as session:
            before_create: int = await session.scalar(func.count(Comment.id))
        res = await ac.post(
            f"events/{event_1.id}/comments",
            headers={**user_1_auth_header},
            json={**create_comment_data}
        )
        get_event = await ac.get(f"events/{event_1.id}")
        event = (get_event.json())
        comments = event.get("comments")
        assert res.status_code == 201
        assert len(comments) - before_create == 1

    async def test_create_comment_has_correct_relations(
            self, create_comment_data, event_1: Event, user_1_auth_header, user_1: Dict, ac: AsyncClient):
        res = await ac.post(
            f"events/{event_1.id}/comments",
            headers={**user_1_auth_header},
            json={**create_comment_data}
        )
        async with async_session_maker() as session:
            comments = await session.execute(select(Comment).join(Event).filter(Comment.event_id == event_1.id))
        comment = comments.scalars().all()[-1]
        print(comment)
        assert res.status_code == 201
        assert comment.event_id == event_1.id
        assert comment.owner_id == user_1.get("id")

    async def test_create_comment_has_correct_username(
            self, user_1_auth_header, create_comment_data, event_1, ac: AsyncClient):
        res = await ac.post(
            f"events/{event_1.id}/comments",
            headers={**user_1_auth_header},
            json={**create_comment_data}
        )
        event = await ac.get(
            f"events/{event_1.id}",
        )
        last_comment = event.json().get("comments")[-1]
        assert last_comment.get("username") == USER_1_USERNAME

    async def test_delete_comment_by_another(self, user_2_auth_header, event_1, comment_1, ac: AsyncClient):
        res = await ac.delete(
            f"events/{event_1.id}/comments/{comment_1.id}",
            headers={**user_2_auth_header}
        )
        async with async_session_maker() as session:
            deleted_comment = await session.scalar(select(Comment.id).where(Comment.id == comment_1.id))
        assert res.status_code == 403
        assert deleted_comment

    async def test_delete_comment_by_anon(self, event_1, comment_1, ac: AsyncClient):
        res = await ac.delete(
            f"events/{event_1.id}/comments/{comment_1.id}",

        )
        async with async_session_maker() as session:
            deleted_comment = await session.scalar(select(Comment.id).where(Comment.id == comment_1.id))
        assert res.status_code == 401
        assert deleted_comment

    async def test_patch_comment_by_anon(
            self, user_1_auth_header, create_comment_data, event_1, comment_1, ac: AsyncClient):
        before_patch_text = comment_1.text
        res = await ac.patch(
            f"events/{event_1.id}/comments/{comment_1.id}",
            json={**create_comment_data}

        )
        async with async_session_maker() as session:
            patched_comment = await session.scalar(select(Comment).where(Comment.id == comment_1.id))
        assert res.status_code == 401
        assert patched_comment.text == before_patch_text

    async def test_patch_comment_by_another(
            self, user_1_auth_header, user_2_auth_header, create_comment_data, event_1, comment_1, ac: AsyncClient):
        before_patched_text = comment_1.text
        res = await ac.patch(
            f"events/{event_1.id}/comments/{comment_1.id}",
            headers={**user_2_auth_header},
            json={**create_comment_data}

        )
        async with async_session_maker() as session:
            pathced_comment = await session.scalar(select(Comment).where(Comment.id == comment_1.id))
        assert res.status_code == 403
        assert before_patched_text == pathced_comment.text


    async def test_patch_comment(
            self, user_2_auth_header,  create_comment_data, event_1, comment_2, ac: AsyncClient):
        before_patch_text = comment_2.text
        res = await ac.patch(
            f"events/{event_1.id}/comments/{comment_2.id}",
            headers={**user_2_auth_header},
            json={**create_comment_data}

        )
        async with async_session_maker() as session:
            patched_comment = await session.scalar(select(Comment).where(Comment.id == comment_2.id))
        assert res.status_code == 200
        assert patched_comment.text != before_patch_text


    async def test_delete_comment(self, user_1_auth_header, event_1, comment_1, ac: AsyncClient):

        res = await ac.delete(
            f"events/{event_1.id}/comments/{comment_1.id}",
            headers={**user_1_auth_header}
        )
        async with async_session_maker() as session:
            deleted_comment = await session.scalar(select(Comment.id).where(Comment.id == comment_1.id))
        assert res.status_code == 200
        assert not deleted_comment






