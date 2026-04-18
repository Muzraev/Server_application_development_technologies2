from fastapi import Header
from pydantic import ValidationError

from errors import AppBadRequest, clean_pydantic_message
from models.headers import CommonHeaders
from models.auth import LoginRequest
from storage import demo_user


def validate_credentials(data: LoginRequest) -> bool:
    return (
        data.username == demo_user["username"]
        and data.password == demo_user["password"]
    )


def get_common_headers(
    user_agent: str = Header(..., alias="User-Agent"),
    accept_language: str = Header(..., alias="Accept-Language"),
) -> CommonHeaders:
    try:
        return CommonHeaders(
            user_agent=user_agent,
            accept_language=accept_language,
        )
    except ValidationError as exc:
        first_error = exc.errors()[0]
        raise AppBadRequest(clean_pydantic_message(first_error["msg"]))