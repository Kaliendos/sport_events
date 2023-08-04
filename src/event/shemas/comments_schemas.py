from uuid import UUID

from pydantic import BaseModel


class ReadComment(BaseModel):
    text: str
    username: str


    class Config:
        orm_mode = True
