import os
from dotenv import load_dotenv

load_dotenv()


class DBConfig:
  database_url = os.getenv("DATABASE_URL")
  refresh_interval = int(os.getenv("TASA_REFRESCO_DATOS", "60")) * 60


class HashConfig:
  time_cost = int(os.getenv("TIME_COST"))
  memory_cost = int(os.getenv("MEMORY_COST"))
  parallelism = int(os.getenv("PARALLELISM"))


class TokenConfig:
  secret_key = os.getenv("SECRET_KEY")
  secret_key_refresh = os.getenv("SECRET_KEY_REFRESH")
  algorithm = os.getenv("ALGORITHM")
  exp_access_token = int(os.getenv("EXPIRATION_ACCESS_TOKEN"))
  exp_refresh_token = int(os.getenv("EXPIRATION_REFRESH_TOKEN"))
  token_type_access = os.getenv("TOKEN_TYPE_ACCES")
  token_type_refresh = os.getenv("TOKEN_TYPE_REFRESH")


class CookieConfig:
    http_only: bool = True
    secure: bool = os.getenv("SECURE", "").strip().lower() in ("1", "true")
    samesite: str = os.getenv("SAMESITE", "lax")
    
class RedisConfig:
    redis_url:str=os.getenv("REDIS_URL")