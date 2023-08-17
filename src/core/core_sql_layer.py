

from abc import ABC, abstractmethod


from fastapi import Depends, HTTPException
from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.event.models import Event


class AbstractCRUD(ABC):
    @abstractmethod
    async def get_one(self, pk):
        raise NotImplementedError

    @abstractmethod
    async def get_all(self):
        raise NotImplementedError

    @abstractmethod
    async def create(self, data):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, obj_id: int):
        raise NotImplementedError

    @abstractmethod
    async def update(self, obj_id: int, data):
        raise NotImplementedError



class CRUDSet(AbstractCRUD):
    """
    Предоставляет базовый интерфейс CRUD для работы с базой данных,
    при необходимости методы можно переопределить.
    """
    model = None

    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.session = session

    async def get_obj_or_404(self,
            model,
            obj_id: int,

    ):
        """
        Ищет модель в базе по параметру obj_id, если не находит - вызывает 404.
        :param model:
        :param obj_id:
        :return obj or 404:
        """

        obj = await self.session.scalar(select(model).where(model.id == obj_id))
        if obj is None:
            raise HTTPException(status_code=404, detail="item not found")
        return obj

    async def get_all(self):
        objects = await self.session.scalars(select(Event))
        return objects.all()

    async def get_one(self, obj_id: int):
        return await self.session.scalar(select(self.model).where(self.model.id == obj_id))

    async def create(self, data):
        query = insert(self.model).values(**data)
        await self.session.execute(query)
        await self.session.commit()

    async def update(self, obj, data):
        self.session.add(obj)
        scheme = data.model_dump(exclude_unset=True)
        for field, value in scheme.items():
            setattr(obj, field, value)
        await self.session.commit()

    async def delete(self, obj):
        await self.session.delete(obj)
        await self.session.commit()

    async def delete_by_id(self, obj_id: int):
        await self.session.execute(delete(Event).where(self.model.id == obj_id))
        await self.session.commit()

    def __call__(self, *args, **kwargs):
        return self.get_obj_or_404(*args, **kwargs)