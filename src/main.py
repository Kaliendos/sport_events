from fastapi import FastAPI

from src.users.auth import auth_backend
from src.users.schemas import UserRead, UserCreate
from src.users.user_manager import fastapi_users
from src.event.routers.event_router import router as event_router
from debug_toolbar.middleware import DebugToolbarMiddleware
from src.event.routers.comment_rourer import router as comment_router

app = FastAPI()
app.add_middleware(
    DebugToolbarMiddleware,
    panels=["debug_toolbar.panels.sqlalchemy.SQLAlchemyPanel"],
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





