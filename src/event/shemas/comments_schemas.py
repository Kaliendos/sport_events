from uuid import UUID

from pydantic import BaseModel


class ReadComment(BaseModel):
    id: int
    text: str
    username: str


    class ConfigDict:
        from_attributes = True



class CreateComment(BaseModel):
    text: str

    class ConfigDict:
        from_attributes = True



class UpdateComment(BaseModel):
    text: str | None

    class ConfigDict:
        from_attributes = True
