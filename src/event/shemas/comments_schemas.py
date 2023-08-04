from uuid import UUID

from pydantic import BaseModel

from src.event.models import User
from src.users.schemas import UserRead


class ReadComment(BaseModel):
    text: str

    class Config:
        orm_mode = True

