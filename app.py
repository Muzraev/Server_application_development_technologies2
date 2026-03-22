import uuid
import time
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Header, Request, Response, Cookie, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr, validator
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

app = FastAPI(title="Контрольная работа №2")

SECRET_KEY = "my-super-secret-key-123"
serializer = URLSafeTimedSerializer(SECRET_KEY)

users_db = {
    "user123": {"username": "user123", "password": "password123", "email": "user@example.com", "name": "Test User"}
}
active_tokens: Dict[str, str] = {}

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = Field(None, ge=1, description="Возраст (положительное целое)")
    is_subscribed: bool = False

@app.post("/create_user", response_model=UserCreate)
def create_user(user: UserCreate):
    """Принимает данные пользователя и возвращает их же."""
    return user

sample_products = [
    {"product_id": 123, "name": "Smartphone", "category": "Electronics", "price": 599.99},
    {"product_id": 456, "name": "Phone Case", "category": "Accessories", "price": 19.99},
    {"product_id": 789, "name": "Iphone", "category": "Electronics", "price": 1299.99},
    {"product_id": 101, "name": "Headphones", "category": "Accessories", "price": 99.99},
    {"product_id": 202, "name": "Smartwatch", "category": "Electronics", "price": 299.99},
]

@app.get("/product/{product_id}")
def get_product(product_id: int):
    """Возвращает продукт по ID."""
    for prod in sample_products:
        if prod["product_id"] == product_id:
            return prod
    raise HTTPException(status_code=404, detail="Product not found")

@app.get("/products/search")
def search_products(keyword: str, category: Optional[str] = None, limit: int = 10):
    """Поиск продуктов по ключевому слову (не чувствителен к регистру) и категории."""
    results = []
    for prod in sample_products:
        if keyword.lower() in prod["name"].lower():
            if category is None or prod["category"].lower() == category.lower():
                results.append(prod)
    return results[:limit]

@app.post("/login_simple")
def login_simple(request: Request, response: Response):
    """Логин, устанавливающий куку session_token с UUID."""
    data = request.json()
    username = data.get("username")
    password = data.get("password")
    user = users_db.get(username)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = str(uuid.uuid4())
    active_tokens[token] = username

    response.set_cookie(key="session_token", value=token, httponly=True, max_age=300)
    return {"message": "Logged in"}

@app.get("/user_simple")
def get_user_simple(session_token: Optional[str] = Cookie(None)):
    """Защищённый маршрут, проверяющий наличие куки session_token."""
    if not session_token or session_token not in active_tokens:
        raise HTTPException(status_code=401, detail="Unauthorized")
    username = active_tokens[session_token]
    user = users_db.get(username, {})
    return {"username": username, "email": user.get("email"), "name": user.get("name")}

def sign_user_id(user_id: str) -> str:
    """Создаёт подпись для user_id в формате <user_id>.<signature>."""
    return serializer.dumps(user_id)

def verify_signed_token(token: str) -> str:
    """Проверяет подпись и возвращает user_id или None."""
    try:
        user_id = serializer.loads(token, max_age=300)
        return user_id
    except (BadSignature, SignatureExpired):
        return None

@app.post("/login_signed")
def login_signed(request: Request, response: Response):
    """Логин с подписанной кукой."""
    data = request.json()
    username = data.get("username")
    password = data.get("password")
    user = users_db.get(username)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Создаём подписанный токен
    token = sign_user_id(username)
    response.set_cookie(key="session_token", value=token, httponly=True, max_age=300)
    return {"message": "Logged in"}

@app.get("/user_signed")
def get_user_signed(session_token: Optional[str] = Cookie(None)):
    """Защищённый маршрут, проверяющий подпись."""
    if not session_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_id = verify_signed_token(session_token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session")
    user = users_db.get(user_id, {})
    return {"username": user_id, "email": user.get("email"), "name": user.get("name")}

def create_signed_session(user_id: str, timestamp: int) -> str:
    """Создаёт подписанную строку в формате user_id.timestamp.signature."""
    data = f"{user_id}.{timestamp}"
    signature = serializer.dumps(data)
    return signature

def parse_signed_session(token: str) -> tuple:
    """Разбирает токен, возвращает (user_id, timestamp) или None."""
    try:
        data = serializer.loads(token, max_age=None)
        parts = data.split('.')
        if len(parts) != 2:
            return None
        user_id = parts[0]
        timestamp = int(parts[1])
        return user_id, timestamp
    except (BadSignature, ValueError):
        return None

def renew_session_if_needed(response: Response, token: str, current_time: int) -> tuple:
    """
    Проверяет время и при необходимости обновляет куку.
    Возвращает (user_id, error_message) если ошибка.
    """
    result = parse_signed_session(token)
    if result is None:
        return None, "Invalid session"
    user_id, last_active = result
    elapsed = current_time - last_active
    if elapsed > 300:
        return None, "Session expired"
    if elapsed >= 180:
        new_token = create_signed_session(user_id, current_time)
        response.set_cookie(key="session_token", value=new_token, httponly=True, max_age=300)
    return user_id, None

@app.post("/login_dynamic")
def login_dynamic(request: Request, response: Response):
    """Логин с динамической сессией."""
    data = request.json()
    username = data.get("username")
    password = data.get("password")
    user = users_db.get(username)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    current_time = int(time.time())
    token = create_signed_session(username, current_time)
    response.set_cookie(key="session_token", value=token, httponly=True, max_age=300)
    return {"message": "Logged in"}

@app.get("/user_dynamic")
def get_user_dynamic(request: Request, response: Response):
    """Защищённый маршрут с проверкой и обновлением сессии."""
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    current_time = int(time.time())
    user_id, error = renew_session_if_needed(response, session_token, current_time)
    if error:
        raise HTTPException(status_code=401, detail=error)
    user = users_db.get(user_id, {})
    return {"username": user_id, "email": user.get("email"), "name": user.get("name")}

class CommonHeaders(BaseModel):
    """Модель для извлечения и валидации заголовков."""
    user_agent: str = Header(..., alias="User-Agent")
    accept_language: str = Header(..., alias="Accept-Language")

    @validator("accept_language")
    def validate_accept_language(cls, v):
        if not v or len(v) < 2:
            raise ValueError("Invalid Accept-Language format")
        import re
        if not re.match(r'^[a-zA-Z0-9\-_,;\.\s=]+$', v):
            raise ValueError("Accept-Language contains invalid characters")
        return v

@app.get("/headers")
def get_headers(headers: CommonHeaders = Depends()):
    """Возвращает заголовки User-Agent и Accept-Language."""
    return {
        "User-Agent": headers.user_agent,
        "Accept-Language": headers.accept_language
    }

@app.get("/info")
def get_info(headers: CommonHeaders = Depends(), response: Response = None):
    """Возвращает сообщение и заголовки, а также добавляет X-Server-Time."""
    current_time = datetime.utcnow().isoformat() + "Z"
    response.headers["X-Server-Time"] = current_time
    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)