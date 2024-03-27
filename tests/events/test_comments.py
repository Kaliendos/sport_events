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


USER_1_USERNAME = "user1@gmail.com"
USER_1_FIRST_NAME = user_1_register_data.get("first_name")
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
    async def test_get_events_comments(
            self, comments_to_event_1, event_1: Event, ac: AsyncClient):
        """Проверяем, что комменатрии создались к нужному событию"""
        EXCEPTED_COMMENT_COUNT: int = 2
        res = await ac.get(f"events/{event_1.id}")
        assert len(res.json().get("comments")) == EXCEPTED_COMMENT_COUNT

    async def test_create_comment(
            self, create_comment_data, event_1: Event, user_1_auth_header, ac: AsyncClient):
        EXCEPTED_DIFFERENCE = 1
        async with async_session_maker() as session:
            before_create = await session.execute(
                select(Comment).where(Comment.event_id == int(event_1.id)))
            before_create_count = len(before_create.scalars().all())
        res = await ac.post(
            f"events/{event_1.id}/comments",
            headers={**user_1_auth_header},
            json={**create_comment_data}
        )
        get_event = await ac.get(f"events/{event_1.id}")
        event = (get_event.json())
        comments = event.get("comments")
        assert res.status_code == status.HTTP_201_CREATED
        assert len(comments) - before_create_count == EXCEPTED_DIFFERENCE, (
            "Проверьте, кто комменатнрий создается в бд"
        )

    async def test_create_comment_has_correct_relations(
            self, create_comment_data, event_1: Event,
            user_1_auth_header, user_1: Dict, ac: AsyncClient):
        res = await ac.post(
            f"events/{event_1.id}/comments",
            headers={**user_1_auth_header},
            json={**create_comment_data}
        )
        async with async_session_maker() as session:
            comments = await (
                session.execute(
                    select(Comment).
                    join(Event).filter(Comment.event_id == int(event_1.id))
                )
            )
        comment = comments.scalars().all()[-1]
        assert res.status_code == status.HTTP_201_CREATED
        assert comment.event_id == event_1.id, (
            "Проверьте, что при создании коменатрия, к нему добавляется корректный event_id"
        )
        assert comment.owner_id == user_1.get("id"), (
            "Проверьте, что при создании коменатрия, к нему добавляется корректный owner_id"
        )

    async def test_create_comment_has_correct_name(
            self, user_1_auth_header, create_comment_data, event_1: Event, ac: AsyncClient):
        await ac.post(
            f"events/{event_1.id}/comments",
            headers={**user_1_auth_header},
            json={**create_comment_data}
        )
        event = await ac.get(
            f"events/{event_1.id}",
        )
        last_comment = event.json().get("comments")[-1]
        assert last_comment.get("name") == USER_1_FIRST_NAME, (
            "Проверьте правильность имени автора комменатрия"
        )

    async def test_delete_comment_by_another(
            self, user_2_auth_header, event_1: Event, comment_1: Comment, ac: AsyncClient):
        res = await ac.delete(
            f"events/{event_1.id}/comments/{comment_1.id}",
            headers={**user_2_auth_header}
        )
        async with async_session_maker() as session:
            deleted_comment = await session.scalar(
                select(Comment.id).where(Comment.id == int(comment_1.id))
            )
        assert res.status_code == status.HTTP_403_FORBIDDEN
        assert deleted_comment, (
            "Проверьте, что комменатрий не может удалятся не автором"
        )

    async def test_delete_comment_by_anon(
            self, event_1: Event, comment_1: Comment, ac: AsyncClient):
        res = await ac.delete(
            f"events/{event_1.id}/comments/{comment_1.id}",

        )
        async with async_session_maker() as session:
            deleted_comment = await session.scalar(
                select(Comment.id).where(Comment.id == int(comment_1.id))
            )
        assert res.status_code == status.HTTP_401_UNAUTHORIZED
        assert deleted_comment, (
            (
                "Проверьте, что комменатрий не может удалятся анонимом"
            )
        )

    async def test_patch_comment_by_anon(
            self, user_1_auth_header, create_comment_data,
            event_1: Event, comment_1: Comment, ac: AsyncClient):
        before_patch_text = comment_1.text
        res = await ac.patch(
            f"events/{event_1.id}/comments/{comment_1.id}",
            json={**create_comment_data}

        )
        async with async_session_maker() as session:
            patched_comment = await session.scalar(
                select(Comment).where(Comment.id == int(comment_1.id)))
        assert res.status_code == status.HTTP_401_UNAUTHORIZED
        assert patched_comment.text == before_patch_text, (
            "Проверьте, что коменатрий не может изменить аноним"
        )

    async def test_patch_comment_by_another(
            self, user_1_auth_header, user_2_auth_header,
            create_comment_data, event_1: Event, comment_1: Comment, ac: AsyncClient):
        before_patched_text = comment_1.text
        res = await ac.patch(
            f"events/{event_1.id}/comments/{comment_1.id}",
            headers={**user_2_auth_header},
            json={**create_comment_data}

        )
        async with async_session_maker() as session:
            pathced_comment = await session.scalar(
                select(Comment).where(Comment.id == int(comment_1.id)))
        assert res.status_code == status.HTTP_403_FORBIDDEN
        assert before_patched_text == pathced_comment.text, (
            "Проверьте, что коменатрий не может изменить не автор"
        )

    async def test_patch_comment(
            self, user_2_auth_header,  create_comment_data,
            event_1: Event, comment_2: Comment, ac: AsyncClient):
        before_patch_text = comment_2.text
        res = await ac.patch(
            f"events/{event_1.id}/comments/{comment_2.id}",
            headers={**user_2_auth_header},
            json={**create_comment_data}
        )
        async with async_session_maker() as session:
            patched_comment = await session.scalar(
                select(Comment).where(Comment.id == int(comment_2.id)))
        assert res.status_code == status.HTTP_200_OK
        assert patched_comment.text != before_patch_text, (
            "Проверьте, что автор может менять свой комментарий"
        )

    async def test_delete_comment(
            self, user_1_auth_header, event_1: Event, comment_1: Comment, ac: AsyncClient):
        res = await ac.delete(
            f"events/{event_1.id}/comments/{comment_1.id}",
            headers={**user_1_auth_header}
        )
        async with async_session_maker() as session:
            deleted_comment = await session.scalar(
                select(Comment.id).where(Comment.id == int(comment_1.id)))
        assert res.status_code == status.HTTP_200_OK
        assert not deleted_comment, (
            "Проверьте, что автор может удалить свой комментарий"
        )
