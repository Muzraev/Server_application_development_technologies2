from datetime import datetime

from fastapi import APIRouter, Depends, Response

from dependencies import get_common_headers
from errors import BAD_REQUEST_DOC
from models.headers import CommonHeaders

router = APIRouter(prefix="/task-5-5", tags=["Задание 5.5"])


@router.get(
    "/headers",
    summary="Получить заголовки через CommonHeaders",
    responses={400: BAD_REQUEST_DOC},
)
async def read_headers_with_model(headers: CommonHeaders = Depends(get_common_headers)):
    return {
        "User-Agent": headers.user_agent,
        "Accept-Language": headers.accept_language,
    }


@router.get(
    "/info",
    summary="Получить информацию и серверное время",
    responses={400: BAD_REQUEST_DOC},
)
async def info_with_headers(
    response: Response,
    headers: CommonHeaders = Depends(get_common_headers),
):
    response.headers["X-Server-Time"] = datetime.now().isoformat(timespec="seconds")

    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language,
        },
    }