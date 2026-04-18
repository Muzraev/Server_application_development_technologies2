from pydantic import BaseModel, ConfigDict, Field, field_validator


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(..., min_length=1, examples=["user123"])
    password: str = Field(..., min_length=1, examples=["password123"])

    @field_validator("username", "password")
    @classmethod
    def validate_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Поле не должно быть пустым")
        return value