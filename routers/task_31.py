from fastapi import APIRouter

from errors import BAD_REQUEST_DOC
from models.user import UserCreate

router = APIRouter(prefix="/task-3-1", tags=["Задание 3.1"])


@router.post(
    "/create_user",
    response_model=UserCreate,
    summary="Создать пользователя",
    responses={400: BAD_REQUEST_DOC},
)
async def create_user(user: UserCreate):
    return user