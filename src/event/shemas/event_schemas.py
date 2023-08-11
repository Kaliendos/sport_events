import datetime
from typing import List
from uuid import UUID


from pydantic import BaseModel

from src.event.shemas.comments_schemas import ReadComment


class LocationModel(BaseModel):
    coordinates: List

    class ConfigDict:
        from_attributes = True


class ReadEvent(BaseModel):
    id: int
    city_id: int
    description: str
    owner_id: UUID
    datetime: datetime.datetime
    location: LocationModel

    class ConfigDict:
        from_attributes = True


class ReadEventItem(ReadEvent):
    comments: List[ReadComment]
    pass


class CreateEvent(BaseModel):
    city_id: int
    description: str
    event_type: str
    location: str

    class ConfigDict:
        from_attributes = True


class UpdateEvent(BaseModel):
    city_id: int | None
    description: str | None
    event_type: str | None
    datetime: datetime.datetime | None
    location: str | None

    class ConfigDict:
        from_attributes = True

