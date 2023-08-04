
from typing import List
from fastapi import APIRouter, Depends

from src.event.db_queries import EventQueries
from src.event.models import Event

from src.event.shemas.event_schemas import ReadEvent, CreateEvent, PatchEvent, ReadEventItem
from src.users.user_manager import current_user
from src.utils import obj_permission

router = APIRouter()


@router.get("/")
async def get_events(query: EventQueries = Depends()) -> List[ReadEvent]:
    return await query.get_events_list()

@router.get("/{event_id}")
async def get_event(event_id: int, query: EventQueries = Depends()) -> ReadEventItem:

    return await query.get_event(event_id)

@router.post("/")
async def post_events(data: CreateEvent, query: EventQueries = Depends(), user=Depends(current_user)):
    datas = data.model_dump()
    datas["owner_id"] = user.id
    print(datas)
    return await query.create_event(datas)


@router.patch("/{obj_id}")
@obj_permission(Event)
async def patch_events(
        obj_id: int,
        data: PatchEvent,
        query: EventQueries = Depends(),
        user=Depends(current_user)):
    return await query.patch_event(obj_id, data)

@router.delete("/{obj_id}")
@obj_permission(Event)
async def delete_event(obj_id: int, query: EventQueries = Depends(), user=Depends(current_user)):
    return await query.delete_event(obj_id)
