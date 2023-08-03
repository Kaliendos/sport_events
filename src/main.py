from fastapi import FastAPI

from src.users.auth import auth_backend
from src.users.schemas import UserRead, UserCreate
from src.users.user_manager import fastapi_users
from src.event.routers.get import router as event_router
app = FastAPI()

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






