import re

from pydantic import BaseModel, field_validator

LANGUAGE_REGEX = re.compile(
    r"^[a-zA-Z]{2,3}(?:-[a-zA-Z]{2})?"
    r"(?:\s*,\s*[a-zA-Z]{2,3}(?:-[a-zA-Z]{2})?"
    r"(?:;q=(?:0(?:\.\d{1,3})?|1(?:\.0{1,3})?))?)*$"
)


class CommonHeaders(BaseModel):
    user_agent: str
    accept_language: str

    @field_validator("user_agent")
    @classmethod
    def validate_user_agent(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("User-Agent не может быть пустым")
        return value

    @field_validator("accept_language")
    @classmethod
    def validate_accept_language(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Accept-Language не может быть пустым")
        if not LANGUAGE_REGEX.fullmatch(value):
            raise ValueError("Неверный формат Accept-Language")
        return value