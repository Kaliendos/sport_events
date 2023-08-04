import datetime
from typing import List
from uuid import UUID


from pydantic import BaseModel

from src.event.shemas.comments_schemas import ReadComment


class LocationModel(BaseModel):
    coordinates: List

    class Config:
        orm_mode = True


class ReadEvent(BaseModel):
    id: int
    city_id: int
    description: str
    owner_id: UUID
    datetime: datetime.datetime
    location: LocationModel
    class Config:
        orm_mode = True


class ReadEventItem(ReadEvent):
    comments: List[ReadComment]

class CreateEvent(BaseModel):
    city_id: int
    description: str
    event_type: str
    datetime: datetime.datetime
    location: str
    class Config:
        orm_mode = True


class PatchEvent(BaseModel):
    city_id: int | None
    description: str | None
    event_type: str | None
    datetime: datetime.datetime | None
    location: str | None

    class Config:
        orm_mode = True

