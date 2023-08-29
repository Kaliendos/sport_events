from uuid import UUID

from fastapi import Depends

from src.event.models import User
from src.users.db_operations import UserCrud
from src.users.schemas import ProfileOtherRead


class UserService:
    def __init__(self, user_crud: UserCrud = Depends()):
        self.user_crud = user_crud

    async def get_user_profile(self, user_id: UUID):
        res = await self.user_crud.get_one(user_id)
        events, user = res
        user["events"] = [_ for _ in events]
        return user

