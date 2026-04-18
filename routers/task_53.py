import time
import uuid

from fastapi import APIRouter, Cookie, Response
from itsdangerous import BadSignature, Signer

from dependencies import validate_credentials
from errors import AppUnauthorized, BAD_REQUEST_DOC, UNAUTHORIZED_DOC
from models.auth import LoginRequest
from storage import SECRET_KEY, demo_user, dynamic_sessions

router = APIRouter(prefix="/task-5-3", tags=["Задание 5.3"])

COOKIE_NAME = "session_token"
COOKIE_PATH = "/task-5-3"
signer = Signer(SECRET_KEY)


@router.post(
    "/login",
    summary="Вход с динамической сессией",
    responses={400: BAD_REQUEST_DOC, 401: UNAUTHORIZED_DOC},
)
async def login_dynamic(data: LoginRequest, response: Response):
    if not validate_credentials(data):
        raise AppUnauthorized("Неверный логин или пароль.")

    user_id = str(uuid.uuid4())
    now_ts = int(time.time())

    dynamic_sessions[user_id] = {
        "user_id": user_id,
        "username": demo_user["username"],
        "email": demo_user["email"],
        "name": demo_user["name"],
    }

    raw_value = f"{user_id}.{now_ts}"
    session_token = signer.sign(raw_value).decode()

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
        "last_activity": now_ts,
    }


@router.get(
    "/profile",
    summary="Профиль с динамическим продлением",
    responses={400: BAD_REQUEST_DOC, 401: UNAUTHORIZED_DOC},
)
async def get_profile_dynamic(
    response: Response,
    session_token: str | None = Cookie(None),
):
    if session_token is None:
        raise AppUnauthorized("Cookie 'session_token' отсутствует.")

    if not session_token.strip():
        raise AppUnauthorized("Cookie 'session_token' пустая.")

    try:
        unsigned_value = signer.unsign(session_token).decode()
    except BadSignature:
        raise AppUnauthorized("Invalid session")

    parts = unsigned_value.rsplit(".", 1)
    if len(parts) != 2:
        raise AppUnauthorized("Invalid session")

    user_id, timestamp_str = parts

    try:
        last_activity = int(timestamp_str)
    except ValueError:
        raise AppUnauthorized("Invalid session")

    now_ts = int(time.time())

    if last_activity > now_ts:
        raise AppUnauthorized("Invalid session")

    elapsed = now_ts - last_activity

    if elapsed >= 300:
        raise AppUnauthorized("Session expired")

    profile = dynamic_sessions.get(user_id)
    if not profile:
        raise AppUnauthorized("Invalid session")

    session_extended = False

    if 180 <= elapsed < 300:
        new_last_activity = now_ts
        new_raw_value = f"{user_id}.{new_last_activity}"
        new_session_token = signer.sign(new_raw_value).decode()

        response.set_cookie(
            key=COOKIE_NAME,
            value=new_session_token,
            httponly=True,
            secure=False,
            max_age=300,
            path=COOKIE_PATH,
        )
        session_extended = True

    return {
        "message": "Профиль успешно загружен.",
        "session_extended": session_extended,
        "profile": profile,
    }


@router.post(
    "/logout",
    summary="Очистить cookie 5.3",
    responses={401: UNAUTHORIZED_DOC},
)
async def logout_dynamic(response: Response):
    response.delete_cookie(key=COOKIE_NAME, path=COOKIE_PATH)
    return {"message": "Cookie очищена."}