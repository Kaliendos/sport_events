from uuid import UUID

from sqlalchemy import Select, text

from src.core.core_sql_layer import CRUDSet
from src.event.models import User, Event


class UserCrud(CRUDSet):
    model = User

    async def get_one(self, obj_id: UUID):
        events = text(f"SELECT  to_jsonb(event.*) FROM event where owner_id = '{obj_id}'")
        events = await self.session.execute(events)
        user = text(f"""SELECT to_jsonb("user".*) FROM "user" WHERE "user".id  = '{obj_id}'""")
        user = await self.session.execute(user)
        return events.scalars().all(), user.scalar()
