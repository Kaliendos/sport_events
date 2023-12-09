import datetime
from typing import List
from uuid import UUID

from asyncpg import Point
from pydantic import BaseModel

from src.event.shemas.comments_schemas import ReadComment

EVENT_JSON_SCHEMA = """'id', event.id,
            'city_id', event.city_id,
            'city', city.title,
            'description', event.description,
            'owner_id', event.owner_id,
            'datetime', event.datetime,
            'location', event.location,
            'publish_date', event.publish_date,
            'owner_name', "user".first_name"""

class LocationModel(BaseModel):
    coordinates: List

    class ConfigDict:
        from_attributes = True


class ReadEvent(BaseModel):
    id: int
    city_id: int
    city: str  # Вычисляется название городо по city_id
    description: str
    owner_id: UUID
    owner_name: str
    datetime: datetime.datetime
    location: LocationModel
    publish_date: str

    class ConfigDict:
        from_attributes = True


class GoingUser(BaseModel):
    first_name: str


class ReadEventItem(ReadEvent):
    comments: List[ReadComment]
    going: List


class CreateEvent(BaseModel):
    city_id: int | None = None
    description: str
    event_type: str
    location: str
    datetime: str | None = None

    class ConfigDict:
        from_attributes = True


class UpdateEvent(BaseModel):
    city_id: int | None = None
    description: str | None = None
    event_type: str | None = None
    location: str | None = None

    class ConfigDict:
        from_attributes = True
