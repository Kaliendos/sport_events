from pydantic import BaseModel


class ReadComment(BaseModel):
    id: int
    text: str
    name: str

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
