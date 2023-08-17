from typing import List
from fastapi import APIRouter, Depends, status

from src.event.services import EventService

from src.event.models import Event, User

from src.event.shemas.event_schemas import ReadEvent, CreateEvent, ReadEventItem, UpdateEvent
from src.users.user_manager import current_user
from src.utils import obj_permission


router = APIRouter(prefix="/events")


@router.get("/")
async def get_events(service: EventService = Depends()) -> List[ReadEvent]:
    return await service.get_all()


@router.get("/{event_id}")
async def get_event(event_id: int, service: EventService = Depends()) -> ReadEventItem:
    return await service.get_one(event_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def post_events(
        data: CreateEvent,
        service: EventService = Depends(),
        user: User = Depends(current_user)):
    return await service.create(data, user)


@router.patch("/{obj_id}")
@obj_permission(Event)
async def patch_events(
        obj_id: int,
        schema: UpdateEvent,
        servie: EventService = Depends(),
        user=Depends(current_user)):
    return await servie.update(obj_id, schema, user)


@router.delete("/{obj_id}")
@obj_permission(Event)
async def delete_event(obj_id: int, servie: EventService = Depends(), user=Depends(current_user)):
    return await servie.delete(obj_id)

