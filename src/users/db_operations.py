from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import text, Select, join

from src.core.core_sql_layer import CRUDSet
from src.event.db_operations import EVENT_LIMIT_DEFAULT
from src.event.models import User, City, Event
from src.event.shemas.event_schemas import EVENT_JSON_SCHEMA


class UserCrud(CRUDSet):
    model = User

    async def get_one(self, obj_id: UUID, offset: int):
        events = text(f"""SELECT json_build_object(
            {EVENT_JSON_SCHEMA}
            ) FROM event INNER JOIN city ON event.city_id = city.id
            INNER JOIN "user" ON event.owner_id = "user".id
             where owner_id = '{obj_id}'  ORDER BY publish_date DESC
            LIMIT {EVENT_LIMIT_DEFAULT} OFFSET {offset}""")
        events = await self.session.execute(events)
        events = events.scalars().all()
        user = text(f"""SELECT json_build_object(
            'city_id', "user".city_id,
            'city', city.title,
            'first_name', "user".first_name,
            'last_name', "user".last_name,
            'date_of_birth', "user".date_of_birth,
            'avatar_image_path', "user".avatar_image_path,
            'is_active', "user".is_active,
            'email', "user".email
         )
         FROM "user" INNER JOIN city ON "user".city_id = city.id
          WHERE "user".id  = '{obj_id}'""")
       # user_city_name = await self.session.scalar(Select(City.title).join(User).where(User.id == obj_id))
        user = await self.session.execute(user)
       # event_city_name = await self.session.execute(Select(City.title).join(Event).where(Event.owner_id == obj_id))
        return events, user.scalar(), #user_city_name, event_city_name.scalars().all()

    async def get_user_by_email(self, email: str):
        user = await self.session.scalar(Select(User.id).where(User.email == email))

        return user