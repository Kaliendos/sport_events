from uuid import UUID

from pydantic import BaseModel


class ReadComment(BaseModel):
    text: str
    username: str

    class ConfigDict:
        from_attributes = True



class CreateComment(BaseModel):
    text: str

    class ConfigDict:
        from_attributes = True

