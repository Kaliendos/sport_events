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
                city_id=random.randrange(1,13),
                description='Бегать',
                event_type='running',
                datetime=datetime.datetime.now(),
                location='POINT(55.676371 37.671569)',
                owner_id="e9be3352-c4a1-4c20-94b0-eecb9d8192e3"

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