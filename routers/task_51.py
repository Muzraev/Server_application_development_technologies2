import uuid

from fastapi import APIRouter, Cookie, Response

from dependencies import validate_credentials
from errors import AppUnauthorized, BAD_REQUEST_DOC, UNAUTHORIZED_DOC
from models.auth import LoginRequest
from storage import demo_user, simple_sessions

router = APIRouter(prefix="/task-5-1", tags=["Задание 5.1"])

COOKIE_NAME = "session_token"
COOKIE_PATH = "/task-5-1"


@router.post(
    "/login",
    summary="Вход без подписи cookie",
    responses={400: BAD_REQUEST_DOC, 401: UNAUTHORIZED_DOC},
)
async def login_simple(data: LoginRequest, response: Response):
    if not validate_credentials(data):
        raise AppUnauthorized("Неверный логин или пароль.")

    session_token = uuid.uuid4().hex
    simple_sessions[session_token] = {
        "username": demo_user["username"],
        "email": demo_user["email"],
        "name": demo_user["name"],
    }

    response.set_cookie(
        key=COOKIE_NAME,
        value=session_token,
        httponly=True,
        secure=False,
        max_age=300,
        path=COOKIE_PATH,
    )

    return {
        "message": "Вход выполнен успешно.",
        "session_token": session_token,
    }


@router.get(
    "/user",
    summary="Получить профиль по простой cookie",
    responses={400: BAD_REQUEST_DOC, 401: UNAUTHORIZED_DOC},
)
async def get_user_simple(session_token: str | None = Cookie(None)):
    if session_token is None:
        raise AppUnauthorized("Cookie 'session_token' отсутствует.")

    if not session_token.strip():
        raise AppUnauthorized("Cookie 'session_token' пустая.")

    if session_token not in simple_sessions:
        raise AppUnauthorized("Недействительная сессия.")

    return simple_sessions[session_token]


@router.post(
    "/logout",
    summary="Очистить cookie 5.1",
    responses={401: UNAUTHORIZED_DOC},
)
async def logout_simple(response: Response):
    response.delete_cookie(key=COOKIE_NAME, path=COOKIE_PATH)
    return {"message": "Cookie очищена."}