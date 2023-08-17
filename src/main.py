from fastapi import FastAPI

from src.users.auth import auth_backend
from src.users.schemas import UserRead, UserCreate
from src.users.user_manager import fastapi_users
from src.event.routers.event_router import router as event_router
from src.event.routers.comment_rourer import router as comment_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(debug=True)

origins = [
    "http://localhost:3000",
    "http://localhost"
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





