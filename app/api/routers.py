"""Главный API-роутер приложения."""

from fastapi import APIRouter

from app.api.endpoints import charity_project, donation
from app.core.user import auth_backend, fastapi_users
from app.schemas.user import UserCreate, UserRead, UserUpdate

main_router = APIRouter()

main_router.include_router(
    charity_project.router,
    prefix="/charity_project",
    tags=["Целевые проекты"],
)

main_router.include_router(
    donation.router,
    prefix="/donation",
    tags=["Пожертвования"],
)

main_router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["Аутентификация"],
)

main_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Аутентификация"],
)

users_router = fastapi_users.get_users_router(UserRead, UserUpdate)

users_router.routes = [
    route
    for route in users_router.routes
    if getattr(route, "name", None) != "users:delete_user"
]

main_router.include_router(
    users_router,
    prefix="/users",
    tags=["Пользователи"],
)
