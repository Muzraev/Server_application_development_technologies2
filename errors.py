from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

BAD_REQUEST_DOC = {
    "description": "Некорректный запрос",
    "content": {
        "application/json": {
            "example": {
                "message": "Некорректный запрос"
            }
        }
    },
}

UNAUTHORIZED_DOC = {
    "description": "Ошибка авторизации",
    "content": {
        "application/json": {
            "example": {
                "message": "Unauthorized"
            }
        }
    },
}

NOT_FOUND_DOC = {
    "description": "Не найдено",
    "content": {
        "application/json": {
            "example": {
                "message": "Объект не найден"
            }
        }
    },
}


class AppBadRequest(Exception):
    def __init__(self, message: str):
        self.message = message


class AppUnauthorized(Exception):
    def __init__(self, message: str):
        self.message = message


class AppNotFound(Exception):
    def __init__(self, message: str):
        self.message = message


def clean_pydantic_message(message: str) -> str:
    prefix = "Value error, "
    if message.startswith(prefix):
        return message[len(prefix):]
    return message


def get_custom_validation_message(path: str, errors: list[dict]) -> str:
    if not errors:
        return "Некорректный запрос."

    error = errors[0]
    error_type = error.get("type", "")
    loc = list(error.get("loc", []))
    field = loc[-1] if loc else None

    # Пустой или битый JSON
    if error_type == "json_invalid":
        if path == "/task-3-1/create_user":
            return "Пустой или некорректный JSON. Передайте данные пользователя."
        if path in {
            "/task-5-1/login",
            "/task-5-2/login",
            "/task-5-3/login",
        }:
            return "Пустой или некорректный JSON. Передайте username и password."
        return "Пустой или некорректный JSON в теле запроса."

    # Отсутствует обязательное поле
    if error_type == "missing":
        if loc and loc[0] == "body":
            if len(loc) == 1:
                if path == "/task-3-1/create_user":
                    return "Тело запроса пустое. Передайте JSON с полями name, email, age, is_subscribed."
                if path in {
                    "/task-5-1/login",
                    "/task-5-2/login",
                    "/task-5-3/login",
                }:
                    return "Тело запроса пустое. Передайте JSON с полями username и password."
                return "Тело запроса обязательно и не может быть пустым."

            if field == "name":
                return "Поле 'name' обязательно."
            if field == "email":
                return "Поле 'email' обязательно."
            if field == "username":
                return "Поле 'username' обязательно."
            if field == "password":
                return "Поле 'password' обязательно."

        if loc and loc[0] == "query":
            if field == "keyword":
                return "Параметр 'keyword' обязателен."
            if field == "limit":
                return "Параметр 'limit' обязателен."
            return f"Параметр '{field}' обязателен."

        if loc and loc[0] == "path":
            if field == "product_id":
                return "Параметр 'product_id' должен быть целым числом."

        if loc and loc[0] == "header":
            if field in {"User-Agent", "user-agent"}:
                return "Заголовок 'User-Agent' обязателен."
            if field in {"Accept-Language", "accept-language"}:
                return "Заголовок 'Accept-Language' обязателен."
            return f"Заголовок '{field}' обязателен."

    # Пустая строка
    if error_type == "string_too_short":
        if field == "name":
            return "Поле 'name' не может быть пустым."
        if field == "username":
            return "Поле 'username' не может быть пустым."
        if field == "password":
            return "Поле 'password' не может быть пустым."
        if field == "keyword":
            return "Параметр 'keyword' не может быть пустым."
        if field == "category":
            return "Параметр 'category' не может быть пустым."

    # Неверный тип int
    if error_type in {"int_parsing", "int_from_float"}:
        if field == "age":
            return "Поле 'age' должно быть целым числом."
        if field == "limit":
            return "Параметр 'limit' должен быть целым числом."
        if field == "product_id":
            return "Параметр 'product_id' должен быть целым числом."

    # Неверный bool
    if error_type == "bool_parsing":
        if field == "is_subscribed":
            return "Поле 'is_subscribed' должно быть true или false."

    # Ограничения чисел
    if error_type in {"greater_than_equal", "greater_than"}:
        if field == "age":
            return "Поле 'age' должно быть положительным целым числом."
        if field == "limit":
            return "Параметр 'limit' должен быть больше 0."

    if error_type in {"less_than_equal", "less_than"}:
        if field == "limit":
            return "Параметр 'limit' слишком большой."

    # Лишние поля
    if error_type == "extra_forbidden":
        return f"Лишнее поле '{field}' недопустимо."

    # Ошибки email
    if field == "email":
        return "Поле 'email' должно содержать корректный email."

    # Ошибки из валидаторов
    if error_type == "value_error":
        return clean_pydantic_message(error.get("msg", "Некорректный запрос."))

    return "Некорректный запрос."


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppBadRequest)
    async def app_bad_request_handler(request: Request, exc: AppBadRequest):
        return JSONResponse(status_code=400, content={"message": exc.message})

    @app.exception_handler(AppUnauthorized)
    async def app_unauthorized_handler(request: Request, exc: AppUnauthorized):
        return JSONResponse(status_code=401, content={"message": exc.message})

    @app.exception_handler(AppNotFound)
    async def app_not_found_handler(request: Request, exc: AppNotFound):
        return JSONResponse(status_code=404, content={"message": exc.message})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = exc.errors()
        message = get_custom_validation_message(request.url.path, errors)
        return JSONResponse(
            status_code=400,
            content={
                "message": message,
                "errors": errors,
            },
        )