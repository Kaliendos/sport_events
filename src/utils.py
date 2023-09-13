from functools import wraps


from fastapi import HTTPException
from sqlalchemy import select

from src.core.database import async_session_maker


async def get_obj_or_404(
        model,
        obj_id: int,

):
    """
    Ищет модель в базе по параметру obj_id, если не находит - вызывает 404.
    :param model:
    :param obj_id:
    :return obj or 404:
    """
    async with async_session_maker() as session:
        obj = await session.scalar(select(model).where(model.id == obj_id))
        if obj is None:
            raise HTTPException(status_code=404, detail="item not found")
        return obj


def obj_permission(object):
    """
    Проверяет авторство объекта.
    Если юзер не является автором объекта, вызывает 403.
    Функция обязательно доллжна принмать агрусенты obj_id и user.
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
            try:
                if obj.owner_id != user.id:
                    raise HTTPException(status_code=403)
            except AttributeError:
                raise AttributeError(
                    f"Объект {object} не имеет поля 'owner_id',"
                    "для исправления ошибки,"
                    "добавьте owner_id в модель")
            return await func(*args, **kwargs)
        return wrapper
    return dec
