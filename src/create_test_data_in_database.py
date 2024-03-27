import asyncio
import datetime
import random

from sqlalchemy import insert

from src.core.database import async_session_maker
from src.event.models import Event, City


def generate_random_date():
    day = str(random.randrange(1,31))
    month = str(random.randrange(1,12))
    hour = str(random.randrange(0,24))
    datas = [month, day, hour]
    for i in range(len(datas)):
        if int(datas[i])< 10:
            datas[i] = "0"+ datas[i]

    ans = f"2022-{datas[0]}-{datas[1]} {datas[2]}:00:00"
    date_object = datetime.datetime.strptime(ans, "%Y-%m-%d %H:%M:%S")
    return  date_object


print(generate_random_date())
async def create_1000_events():
    for i in range(100):
        async with async_session_maker() as session:
            await session.execute(insert(Event).values(
                city_id=random.randrange(1, 13),
                description='Бегать',
                event_type='running',
                datetime=generate_random_date(),
                location='Point(55.676371 37.671569)',
                owner_id="e96d6690-73ee-4954-8bce-0e9c98f742f4"

            ))
            await session.commit()


async def create_11_cities():
    cities_name = (
        "Санкт Петербург", "Калининград", "Казань",
        "Нижний Новгород", "Новосибирск", "Тула"
        "Тверь", "Владивосток", "Сочи", "Ростов", "Краснодар"
    )
    for city in cities_name:
        async with async_session_maker() as session:
            await session.execute(insert(City).values(
                title=city
            ))
            await session.commit()


asyncio.run(create_1000_events())
