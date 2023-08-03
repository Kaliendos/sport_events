import datetime
from typing import List, Dict
from uuid import UUID


from pydantic import BaseModel



class LocationModel(BaseModel):
    coordinates: List

    class Config:
        orm_mode = True


class ResponseModel(BaseModel):
    id: int
    city_id: int
    description: str
    owner_id: UUID
    datetime: datetime.datetime
    location: LocationModel

    class Config:
        orm_mode = True


class CreateEvent(BaseModel):
    city_id: int
    description: str
    event_type: str
    datetime: datetime.datetime
    location: str

    class Config:
        orm_mode = True

