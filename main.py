from fastapi import FastAPI

from errors import register_exception_handlers
from routers.task_31 import router as task_31_router
from routers.task_32 import router as task_32_router
from routers.task_51 import router as task_51_router
from routers.task_52 import router as task_52_router
from routers.task_53 import router as task_53_router
from routers.task_54 import router as task_54_router
from routers.task_55 import router as task_55_router

tags_metadata = [
    {"name": "Задание 3.1", "description": "Создание пользователя"},
    {"name": "Задание 3.2", "description": "Получение товара по id и поиск товаров"},
    {"name": "Задание 5.1", "description": "Cookie-аутентификация без подписи"},
    {"name": "Задание 5.2", "description": "Cookie-аутентификация с подписью"},
    {"name": "Задание 5.3", "description": "Cookie-аутентификация с продлением сессии"},
    {"name": "Задание 5.4", "description": "Работа с заголовками"},
    {"name": "Задание 5.5", "description": "CommonHeaders и переиспользование"},
]

app = FastAPI(
    title="Кр №2",
    version="1.0.0",
    description="Задания.",
    openapi_tags=tags_metadata,
)

register_exception_handlers(app)


@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "Сервер работает",
        "docs": "/docs",
        "ping": "/ping",
    }


@app.get("/ping", include_in_schema=False)
async def ping():
    return {"status": "ok"}


app.include_router(task_31_router)
app.include_router(task_32_router)
app.include_router(task_51_router)
app.include_router(task_52_router)
app.include_router(task_53_router)
app.include_router(task_54_router)
app.include_router(task_55_router)