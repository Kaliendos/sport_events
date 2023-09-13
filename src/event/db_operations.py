from sqlalchemy import text, Select

from src.core.core_sql_layer import CRUDSet
from src.event.models import Event, Comment, City


EVENT_LIMIT_DEFAULT: int = 10


class EventCRUD(CRUDSet):
    model = Event

    async def get_one(self, event_id: int):
        get_event_by_id = text(
            f'''
            SELECT  json_build_object(
                'id', event.id,
                'city_id', event.city_id,
                'city', city.title,
                'description', event.description,
                'owner_id', event.owner_id,
                'datetime', event.datetime,
                'location', event.location
            ) FROM event INNER JOIN city
            ON event.city_id = city.id
                 WHERE event.id = {event_id}
            '''
        )
        get_going_users = text(
            f"""
            SELECT json_build_object('id', id, 'name', first_name) from "user"
            INNER JOIN going_table ON going_table.user_id = "user".id
            WHERE going_table.event_id = {event_id}
            """)
        get_event_comments = text(
            f"""
                SELECT json_build_object(
                'text', comment.text,
                'name', "user".first_name,
                'id', comment.id
                ) FROM comment
                INNER JOIN event ON comment.event_id = event.id
                JOIN "user" ON "user".id = comment.owner_id
                WHERE event.id = {event_id}
            """
        )
        event = await self.session.execute(get_event_by_id)
        comments = await self.session.execute(get_event_comments)
        going_users = await self.session.execute(get_going_users)
        going_users = going_users.scalars().all()
        event = event.scalar()
        return event, comments.scalars().all(), going_users

    async def get_all(self, offset: int, city_id: int):
        """

        :param offset: Число с которого делать выборку в базе, по умолчанию - 0
        :param city_id:
        :return:
        """
        get_events_list = text(
            f"""
            SELECT json_build_object(
            'id', event.id,
            'city_id', event.city_id,
            'city', city.title,
            'description', event.description,
            'owner_id', event.owner_id,
            'datetime', event.datetime,
            'location', event.location
            )
            FROM event INNER JOIN city ON event.city_id = city.id  WHERE city_id = {city_id} ORDER BY datetime DESC
            LIMIT {EVENT_LIMIT_DEFAULT} OFFSET {offset}
                """
        )
        events = await self.session.execute(get_events_list)
        return events.scalars().all()


class CommentCrud(CRUDSet):
    model = Comment
