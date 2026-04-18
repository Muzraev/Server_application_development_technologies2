from fastapi import APIRouter, Header
from pydantic import ValidationError

from errors import AppBadRequest, BAD_REQUEST_DOC, clean_pydantic_message
from models.headers import CommonHeaders

router = APIRouter(prefix="/task-5-4", tags=["Задание 5.4"])


@router.get(
    "/headers",
    summary="Получить заголовки",
    responses={400: BAD_REQUEST_DOC},
)
async def read_headers(
    user_agent: str = Header(..., alias="User-Agent"),
    accept_language: str = Header(..., alias="Accept-Language"),
):
    try:
        headers = CommonHeaders(
            user_agent=user_agent,
            accept_language=accept_language,
        )
    except ValidationError as exc:
        first_error = exc.errors()[0]
        raise AppBadRequest(clean_pydantic_message(first_error["msg"]))

    return {
        "User-Agent": headers.user_agent,
        "Accept-Language": headers.accept_language,
    }