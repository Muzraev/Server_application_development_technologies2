from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, examples=["Alice"])
    email: EmailStr = Field(..., examples=["alice@example.com"])
    age: int | None = Field(None, ge=1, examples=[30])
    is_subscribed: bool = Field(False, examples=[True])

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Имя не может быть пустым")
        return value