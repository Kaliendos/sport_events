import os

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from src.users.auth import auth_backend
from src.users.schemas import UserRead, UserCreate
from src.users.user_manager import fastapi_users
from src.event.routers.event_router import router as event_router
from src.event.routers.comment_router import router as comment_router
from fastapi.middleware.cors import CORSMiddleware
from src.users.routers import user_router
from  src.event.routers.cities import  router as city_router

from fastapi.staticfiles import StaticFiles


app = FastAPI(debug=True)
app.mount("/static", StaticFiles(directory="src/static"), name="static")


origins = [
    "http://localhost:3000",
    "http://localhost",
    "*"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)


app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(event_router)
app.include_router(comment_router)
app.include_router(user_router)
app.include_router(city_router)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

@app.get("/1")
async def good():
    return  1

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
