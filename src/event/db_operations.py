from sqlalchemy import text, Select

from src.core.core_sql_layer import CRUDSet
from src.event.models import Event, Comment, City


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
        city_name = await self.session.scalar(Select(City.title).join(Event).where(Event.id == event_id))
        return event.scalar(), comments.scalars().all(), city_name

    async def get_all(self, offset, city_id: int):
        sql = text(
            f"""
            SELECT to_jsonb(event.*)
            FROM event  WHERE city_id = {city_id} ORDER BY datetime
            LIMIT {EVENT_LIMIT_DEFAULT} OFFSET {offset}
                """
        )
        events = await self.session.execute(sql)
        city_name: str = await self.session.scalar(Select(City.title).where(City.id == city_id))
        return events.scalars().all(), city_name


class CommentCrud(CRUDSet):
    model = Comment
