from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth_router, order_router
from fastapi.openapi.docs import get_redoc_html


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)

# Подключение роутеров для аутентификации и заказов
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(order_router, prefix="/api/v1/orders", tags=["orders"])


# Разрешённые домены для CORS
origins = [
    "http://localhost:3000",   # фронтенд для разработки
    "https://myfrontend.com",  # фронтенд в продакшене
]

# Добавление middleware для защиты CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # разрешённые домены
    allow_credentials=True,         # поддержка cookies/авторизации
    allow_methods=["GET", "POST", "PATCH", "DELETE"],  # разрешённые HTTP-методы
    allow_headers=["*"],            # разрешённые заголовки
)


# Простой тестовый эндпоинт
@app.get("/")
def hello_index():
    return {
        "message": "Hello index!",
    }


# Кастомная документация Redoc
@app.get("/custom-redoc", include_in_schema=False)
async def custom_redoc():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="Lead Service API",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2/bundles/redoc.standalone.js",
        redoc_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
        with_google_fonts=True,
    )
