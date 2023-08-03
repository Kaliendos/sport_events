from fastapi import Depends
from sqlalchemy import text, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.event.models import Event
from src.event.schemas import  CreateEvent


class EventQueries:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.session = session

    async def get_events_list(self):
        sql = text(
            'SELECT  to_jsonb(event.*) FROM event'
        )
        events = await self.session.execute(sql)
        return list(events.scalars())

    async def create_event(self, data: CreateEvent):
        query = insert(Event).values(**data)
        await self.session.execute(query)
        await self.session.commit()
