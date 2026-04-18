import uuid

from fastapi import APIRouter, Cookie, Response
from itsdangerous import BadSignature, Signer

from dependencies import validate_credentials
from errors import AppUnauthorized, BAD_REQUEST_DOC, UNAUTHORIZED_DOC
from models.auth import LoginRequest
from storage import SECRET_KEY, demo_user, signed_sessions

router = APIRouter(prefix="/task-5-2", tags=["Задание 5.2"])

COOKIE_NAME = "session_token"
COOKIE_PATH = "/task-5-2"
signer = Signer(SECRET_KEY)


@router.post(
    "/login",
    summary="Вход с подписанной cookie",
    responses={400: BAD_REQUEST_DOC, 401: UNAUTHORIZED_DOC},
)
async def login_signed(data: LoginRequest, response: Response):
    if not validate_credentials(data):
        raise AppUnauthorized("Неверный логин или пароль.")

    user_id = str(uuid.uuid4())
    signed_sessions[user_id] = {
        "user_id": user_id,
        "username": demo_user["username"],
        "email": demo_user["email"],
        "name": demo_user["name"],
    }

    session_token = signer.sign(user_id).decode()

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
        "user_id": user_id,
    }


@router.get(
    "/profile",
    summary="Профиль по подписанной cookie",
    responses={400: BAD_REQUEST_DOC, 401: UNAUTHORIZED_DOC},
)
async def get_profile_signed(session_token: str | None = Cookie(None)):
    if session_token is None:
        raise AppUnauthorized("Cookie 'session_token' отсутствует.")

    if not session_token.strip():
        raise AppUnauthorized("Cookie 'session_token' пустая.")

    try:
        user_id = signer.unsign(session_token).decode()
    except BadSignature:
        raise AppUnauthorized("Подпись cookie недействительна.")

    profile = signed_sessions.get(user_id)
    if not profile:
        raise AppUnauthorized("Сессия не найдена.")

    return profile


@router.post(
    "/logout",
    summary="Очистить cookie 5.2",
    responses={401: UNAUTHORIZED_DOC},
)
async def logout_signed(response: Response):
    response.delete_cookie(key=COOKIE_NAME, path=COOKIE_PATH)
    return {"message": "Cookie очищена."}