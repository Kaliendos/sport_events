import datetime
import uuid
from typing import List

from fastapi_users import schemas
from pydantic import BaseModel

from src.event.shemas.event_schemas import ReadEvent


class UserRead(schemas.BaseUser[uuid.UUID]):
    city_id: int
    first_name: str
    last_name: str
    date_of_birth: datetime.date


class ProfileOtherRead(BaseModel):
    city_id: int
    first_name: str
    city: str  # Вычисляетя название городо по city_id
    last_name: str
    date_of_birth: datetime.date
    events: List[ReadEvent]
    events: List[ReadEvent]
    avatar_image_path: str | None = None
    is_active: bool = True

    class ConfigDict:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    city_id: int
    first_name: str
    last_name: str
    date_of_birth: datetime.date
    avatar_image_path: str | None = None


class UserUpdate(schemas.BaseUserUpdate):
    first_name: str | None = None
    last_name: str | None = None
    city_id: int | None = None
    avatar_image_path: str | None = None
