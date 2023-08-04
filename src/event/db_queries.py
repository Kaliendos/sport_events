from fastapi import Depends, HTTPException
from sqlalchemy import text, insert, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.event.models import Event
from src.event.shemas.event_schemas import CreateEvent, PatchEvent



class EventQueries:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.session = session

    async def get_event_or_404(self, event_id: int):
        event = await self.session.scalar(select(Event).where(Event.id == event_id))
        if event is None:
            raise HTTPException(status_code=404)
        return event

    async def get_events_list(self):
        sql = text(
            'SELECT  to_jsonb(event.*) FROM event'
        )
        events = await self.session.execute(sql)
        return list(events.scalars())

    async def get_event(self, event_id: int):

        sql = text(
            f'''
           SELECT  to_jsonb(event.*) FROM event where id = {event_id}
            '''
        )
        comments = text(
            f"""
                SELECT to_jsonb(comment.*) FROM comment
                INNER JOIN event ON comment.event_id = event.id WHERE event.id = {event_id}
            """
        )
        event = await self.session.execute(sql)
        comments = await self.session.execute(comments)
        event = event.scalar()
        comments = comments.scalars()
        if event is None:
            raise HTTPException(status_code=404)
        event["comments"] = [comment for comment in comments]
        return event

    async def create_event(self, data: CreateEvent):
        query = insert(Event).values(**data)
        await self.session.execute(query)
        await self.session.commit()

    async def patch_event(self, event_id: int, data: PatchEvent):
        scheme = data.model_dump(exclude_unset=True)
        event_obj = await self.get_event_or_404(event_id)
        for field, value in scheme.items():
            setattr(event_obj, field, value)
        await self.session.commit()
        return event_obj

    async def delete_event(self, event_id: int):
        await self.session.execute(delete(Event).where(Event.id == event_id))
        await self.session.commit()


