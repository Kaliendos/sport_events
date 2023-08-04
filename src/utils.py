from functools import wraps

from fastapi import HTTPException
from sqlalchemy import select

from src.core.database import async_session_maker


async def get_obj_or_404(
        obj,
        obj_id: int,
):

    async with async_session_maker() as session:
        obj = await session.scalar(select(obj).where(obj.id == obj_id))
        if obj is None:
            raise HTTPException(status_code=404, detail="item not found")
        return obj


def obj_permission(object):
    """
     Задает право на взаимодействие с объектом только автору этого объекта.

    :param object: Модель бд
    """
    def dec(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            obj_id = kwargs.get("obj_id")
            user = kwargs.get("user")
            if obj_id is None:
                raise KeyError("Остутсвует ключ obj_id в аргументе")
            if user is None:
                raise KeyError("Остутсвует ключ user в аргументе")
            obj = await get_obj_or_404(object, obj_id)
            if obj.owner_id != user.id:
                raise HTTPException(status_code=403)
            return await func(*args, **kwargs)
        return wrapper
    return dec
