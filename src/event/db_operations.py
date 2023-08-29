from sqlalchemy import text, select

from src.core.core_sql_layer import CRUDSet
from src.event.models import Event, Comment

from fastapi_pagination.ext.sqlalchemy import paginate
EVENT_LIMIT_DEFAULT: int = 10


class EventCRUD(CRUDSet):
    model = Event

    async def get_one(self, event_id: int):
        sql = text(
            f'''
                 SELECT  to_jsonb(event.*) FROM event where id = {event_id}
                  '''
        )
        comments = text(
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
        event = await self.session.execute(sql)
        comments = await self.session.execute(comments)
        return event.scalar(), comments.scalars().all()

    async def get_all(self, offset, city_id: int):
        sql = text(
            f"""
            SELECT to_jsonb(event.*)
            FROM event  WHERE city_id = {city_id} ORDER BY datetime
            LIMIT {EVENT_LIMIT_DEFAULT} OFFSET {offset}
                """
        )
        events = await self.session.execute(sql)
        return events.scalars().all()


class CommentCrud(CRUDSet):
    model = Comment
