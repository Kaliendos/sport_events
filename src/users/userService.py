from uuid import UUID

from fastapi import Depends, HTTPException

from src.event.models import  City
from src.users.db_operations import UserCrud

from fastapi.responses import FileResponse


class UserService:
    def __init__(self, user_crud: UserCrud = Depends()):
        self.user_crud = user_crud

    async def check_email_not_exists(self, email: str) -> bool:
        user = await self.user_crud.get_user_by_email(email)
        if user:
            return False
        return True

    async def get_user_profile(self, user_id: UUID, offset: int):
        path_to_image = "../static/images/fillip.jpeg"
        res = await self.user_crud.get_one(user_id, offset)
        # events, user, city_title, event_city_name = res
        events, user = res
        print(events)
        if user is None:
            raise HTTPException(status_code=404)
        user["events"] = [_ for _ in events]
       # user["city"] = city_title
        #for i in range(len(events)):
           # events[i]["city"] = event_city_name[i]
        return user

    async def update_user_profile(self, user, schema):
        city_id_input: int = schema.model_dump().get("city_id")
        await self.user_crud.get_obj_by_id_or_404(City, city_id_input)  # Проверка наличия города
        return await self.user_crud.update(user, schema)
