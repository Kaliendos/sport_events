from uuid import UUID

from fastapi import Depends, HTTPException

from src.event.models import  City
from src.users.db_operations import UserCrud


class UserService:
    def __init__(self, user_crud: UserCrud = Depends()):
        self.user_crud = user_crud

    # offset нужен для частичной выборки из Events пользователя из бд
    async def get_user_profile(self, user_id: UUID, offset: int):
        res = await self.user_crud.get_one(user_id, offset)
        events, user, city_title, event_city_name = res
        if user is None:
            raise HTTPException(status_code=404)
        user["events"] = [_ for _ in events]
        user["city"] = city_title
        for i in range(len(events)):
            events[i]["city"] = event_city_name[i]
        return user

    async def update_user_profile(self, user, schema):
        city_id_input: int = schema.model_dump().get("city_id")
        await self.user_crud.get_obj_by_id_or_404(City, city_id_input)  # Проверка наличия города
        return await self.user_crud.update(user, schema)