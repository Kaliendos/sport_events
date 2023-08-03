from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends

from src.event.db_queries import EventQueries
from src.event.schemas import ResponseModel, CreateEvent
from src.users.user_manager import current_user

router = APIRouter()

@router.get("/")
async def get_events(query: EventQueries = Depends()) -> List[ResponseModel]:
    return await query.get_events_list()


@router.post("/")
async def post_events(data: CreateEvent, query: EventQueries = Depends(), user=Depends(current_user)):

    datas = data.model_dump()
    user_id = user.id
    print(user_id)
    datas["owner_id"] = user.id
    print(datas)
    return await query.create_event(datas)

