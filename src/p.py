import asyncio
import datetime
import random

from sqlalchemy import insert

from src.core.database import async_session_maker
from src.event.models import Event, City


async def create_1000_events():
    for i in range(1000):
        async with async_session_maker() as session:
            await session.execute(insert(Event).values(
                city_id=random.randrange(1,12),
                description='Бегать',
                event_type='running',
                datetime=datetime.datetime.now(),
                location='POINT(55.676371 37.671569)',
                owner_id="e96d6690-73ee-4954-8bce-0e9c98f742f4"

            ))
            await session.commit()


async def create_11_cities():
    cities_name = (
        "Санкт Петербург", "Калининград", "Казань", "Нижний Новгород", "Новосибирск",
        "Тула", "Тверь", "Владивосток", "Сочи", "Ростов", "Краснодар"
    )
    for city in cities_name:
        async with async_session_maker() as session:
            await session.execute(insert(City).values(
                title=city
            ))
            await session.commit()


asyncio.run(create_1000_events())