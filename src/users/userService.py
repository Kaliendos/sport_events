from uuid import UUID

from fastapi import Depends

from src.event.models import  City
from src.users.db_operations import UserCrud


class UserService:
    def __init__(self, user_crud: UserCrud = Depends()):
        self.user_crud = user_crud

    async def get_user_profile(self, user_id: UUID, offset):
        res = await self.user_crud.get_one(user_id, offset)
        events, user, city, event_city_name = res
        user["events"] = [_ for _ in events]
        user["city"] = city
        for i in range(len(events)):
            events[i]["city"] = event_city_name[i]
        return user

    async def update_user_profile(self, user, schema):
        city_id_input: int = schema.model_dump().get("city_id")
        await self.user_crud.get_obj_or_404(City, city_id_input)  # Проверка наличия города
        return await self.user_crud.update(user, schema)