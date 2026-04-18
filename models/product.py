from pydantic import BaseModel, ConfigDict, Field, field_validator


class Product(BaseModel):
    product_id: int
    name: str
    category: str
    price: float


class ProductSearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    keyword: str = Field(..., min_length=1, examples=["phone"])
    category: str | None = Field(None, min_length=1, examples=["Electronics"])
    limit: int = Field(10, ge=1, le=100, examples=[5])

    @field_validator("keyword")
    @classmethod
    def validate_keyword(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Параметр 'keyword' не может быть пустым.")
        return value

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Параметр 'category' не может быть пустым.")
        return value