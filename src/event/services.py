import datetime
from typing import List, Dict

from fastapi import Depends, HTTPException

from src.event.models import Event, User, Comment
from src.event.shemas.comments_schemas import CreateComment, UpdateComment
from src.event.shemas.event_schemas import ReadEvent, CreateEvent, UpdateEvent
from src.event.db_operations import EventCRUD, CommentCrud

from src.utils import get_obj_or_404


class EventService:
    """Слой бизнес логики"""
    def __init__(self, event_crud: EventCRUD = Depends()):
        self.event_crud = event_crud

    async def get_all(self) -> List[ReadEvent]:
        return await self.event_crud.get_all()

    async def get_one(self, pk: int):
        query = await self.event_crud.get_one(pk)
        event, comments = query
        if event is None:
            raise HTTPException(status_code=404)
        event["comments"] = [comment for comment in comments]
        return event

    async def create(self, data: CreateEvent, user: User):
        data = data.model_dump()
        data["owner_id"] = user.id
        data["datetime"] = datetime.datetime.now()
        return await self.event_crud.create(data)

    async def update(self, obj_id: int, data: UpdateEvent, user: User):
        obj = await get_obj_or_404(Event, obj_id)
        return await self.event_crud.update(obj, data)

    async def delete(self, obj_id: int):
        event = await self.event_crud.get_obj_or_404(Event, obj_id)
        return await self.event_crud.delete(event)


class CommentService:
    def __init__(self, comment_crud: CommentCrud = Depends()):
        self.comment_crud = comment_crud

    async def create(self, schema: CreateComment, user, event_id: int):
        data: Dict = schema.model_dump()
        data["owner_id"] = user.id
        data["event_id"] = event_id
        await self.comment_crud.create(data)

    async def delete(self, obj_id: int, event_id: int):
        event = await get_obj_or_404(Event, event_id)
        comments = event.comments
        comments = [comment for comment in comments if comment.id == obj_id] # селекция нужного комментария
        if len(comments) == 0:
            raise HTTPException(status_code=404)
        return await self.comment_crud.delete(comments.pop())

    async def update(self, obj_id: int, data: UpdateComment):
        obj = await self.comment_crud.get_obj_or_404(Comment, obj_id)
        return await self.comment_crud.update(obj, data)