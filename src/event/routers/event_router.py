from typing import List
from sqlalchemy import and_
from fastapi import APIRouter, Depends, status
from sqlalchemy import insert, select, delete

from src.core.database import async_session_maker
from src.event.services import EventService
from fastapi_cache.decorator import cache
from src.event.models import Event, User, going_table

from src.event.shemas.event_schemas import ReadEvent, CreateEvent, ReadEventItem, UpdateEvent
from src.users.user_manager import current_user, current_user_optional
from src.utils import obj_permission

DEFAULT_CITY_ID = 1


router = APIRouter(prefix="/events")


@router.get("/")
#@cache(expire=90)
async def get_events(
        offset: int = 0,
        city_id: int = DEFAULT_CITY_ID,
        user: User = Depends(current_user_optional),
        service: EventService = Depends()) -> List[ReadEvent]:
    return await service.get_all(offset, city_id, user)


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


@router.post("/going/{obj_id}")
async def going_on_event(obj_id: int, user=Depends(current_user)):
    async with async_session_maker() as session:
        event = await session.scalar(select(Event).where(Event.id == obj_id))
        await session.execute(insert(going_table).values(event_id=event.id, user_id=user.id))
        await session.commit()


@router.delete("/going/{obj_id}")
async def going_on_event(obj_id: int, user=Depends(current_user)):
    async with async_session_maker() as session:
        await session.execute(delete(going_table).filter(
        and_(going_table.c.user_id == user.id, going_table.c.event_id == obj_id)))

        await session.commit()
