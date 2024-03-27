import enum
from typing import List
import datetime as dt
from sqlalchemy.sql import func

from sqlalchemy import (
    Column, Table, Integer, ForeignKey, DateTime, Enum, String, Date
)

from geoalchemy2 import Geometry

from fastapi import Depends
from fastapi_users_db_sqlalchemy import (
    SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base, get_async_session


going_table = Table(
    "going_table",
    Base.metadata,
    Column("event_id", Integer, ForeignKey("event.id")),
    Column("user_id", UUID, ForeignKey("user.id")),
)


class User(SQLAlchemyBaseUserTableUUID, Base):
    user_events = relationship(
        "Event", back_populates="owner", lazy="joined"
    )
    event = relationship("Event", secondary=going_table)
    city_id = Column(Integer, ForeignKey("city.id"))
    comments = relationship(
        "Comment", cascade="all, delete", back_populates="author"
    )
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    avatar_image_path = Column(String(300), nullable=True)


class EventType(enum.Enum):
    cycling: str = "cycling"
    running: str = "running"
    workout: str = "workout"


class City(Base):
    __tablename__ = "city"
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    events = relationship("Event", cascade="all, delete")
    dwellers = relationship("User")

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title


class Event(Base):
    __tablename__ = "event"
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(Enum(EventType), default=EventType.cycling)
    owner_id = Column(UUID, ForeignKey("user.id", ondelete="CASCADE"))
    publish_date = Column(DateTime, default=dt.datetime.now(), index=True)
    datetime = Column(DateTime)
    location = Column(Geometry("POINT", srid=4326))
    description = Column(String(380))
    city_id = Column(Integer, ForeignKey("city.id", ondelete="CASCADE"))
    going: Mapped[List[User]] = relationship(
        secondary=going_table, back_populates="event"
    )
    comments = relationship(
        "Comment", back_populates="event", cascade="all, delete", lazy="joined"
    )
    owner = relationship("User")


class Comment(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("event.id", ondelete="CASCADE"))
    event = relationship("Event", back_populates="comments")
    owner_id = Column(UUID, ForeignKey("user.id", ondelete="CASCADE"))
    author = relationship("User", back_populates="comments")
    text = Column(String(300))


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
