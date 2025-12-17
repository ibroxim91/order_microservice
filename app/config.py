import os
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import redis.asyncio as redis
load_dotenv()

DB_PATH = os.getenv("DATABASE_URL")
REDIS_HOST = os.getenv("REDIS_HOST")

REDIS_CLIENT = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

DB_PATH = os.getenv("DATABASE_URL")


class DbSettings(BaseModel):
    url: str = DB_PATH
    # echo: bool = False
    echo: bool = True


class Settings(BaseSettings):
    api_v1_prefix: str = "/api/v1"

    db: DbSettings = DbSettings()

    # db_echo: bool = True


settings = Settings()