from fastapi import APIRouter, Depends

from src.event.models import User, Comment
from src.event.services import CommentService
from src.event.shemas.comments_schemas import CreateComment, UpdateComment
from src.users.user_manager import current_user
from src.utils import obj_permission

router = APIRouter(prefix="/events")


@router.post("/{event_id}/comments", status_code=201)
async def create_comment(
        schema: CreateComment,
        event_id: int,
        service: CommentService = Depends(),
        user=Depends(current_user),
):
    return await service.create(schema, user, event_id)


@router.delete("/{event_id}/comments/{obj_id}")
@obj_permission(Comment)
async def delete_comment(
        event_id: int,
        obj_id: int,
        service: CommentService = Depends(),
        user: User = Depends(current_user),
):
    return await service.delete(obj_id, event_id)


@router.patch("/{event_id}/comments/{obj_id}")
@obj_permission(Comment)
async def update_comment(
        obj_id: int,
        schema: UpdateComment,
        service: CommentService = Depends(),
        user=Depends(current_user)):
    return await service.update(obj_id, schema)
