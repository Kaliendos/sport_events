from uuid import UUID

from fastapi import APIRouter, Depends, status


from src.event.models import User
from src.users.schemas import UserRead, ProfileOtherRead, UserUpdate
from src.users.userService import UserService
from src.users.user_manager import current_user

user_router = APIRouter(prefix="/users")


@user_router.get("/me")
async def users_me(
        user: User = Depends(current_user),
        service: UserService = Depends(),
        offset: int = 0
) -> UserRead:
    return await service.get_user_profile(user.id, offset)


@user_router.get("/{user_id}")
async def other_user_profile(
        user_id: UUID,
        service: UserService = Depends(),
        offset: int = 0
) -> ProfileOtherRead:
    return await service.get_user_profile(user_id, offset)


@user_router.patch("/me")
async def update_profile(schema: UserUpdate, service: UserService = Depends(), user: User = Depends(current_user)):
    return await service.update_user_profile(user, schema)


