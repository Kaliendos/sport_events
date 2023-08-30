from uuid import UUID

from sqlalchemy import text, Select, join

from src.core.core_sql_layer import CRUDSet
from src.event.db_operations import EVENT_LIMIT_DEFAULT
from src.event.models import User, City, Event


class UserCrud(CRUDSet):
    model = User

    async def get_one(self, obj_id: UUID, offset: int):
        events = text(f"""SELECT  to_jsonb(event.*) FROM event where owner_id = '{obj_id}' ORDER BY datetime
            LIMIT {EVENT_LIMIT_DEFAULT} OFFSET {offset}""")
        events = await self.session.execute(events)
        events = events.scalars().all()
        user = text(f"""SELECT to_jsonb("user".*) FROM "user" WHERE "user".id  = '{obj_id}'""")
        user_city_name = await self.session.scalar(Select(City.title).join(User).where(User.id == obj_id))
        user = await self.session.execute(user)
        event_city_name = await self.session.execute(Select(City.title).join(Event).where(Event.owner_id == obj_id))
        return events, user.scalar(), user_city_name, event_city_name.scalars().all()
