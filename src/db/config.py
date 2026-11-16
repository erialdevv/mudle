import os
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL")
refresh_interval = int(os.getenv("TASA_REFRESCO_DATOS", "60")) * 60
time_cost_env=int(os.getenv("TIME_COST"))
memory_cost_env=int(os.getenv("MEMORY_COST"))
parallelism_env=int(os.getenv("PARALLELISM"))
secret_key_env=os.getenv("SECRET_KEY")
algorithm_env=os.getenv("ALGORITHM")
exp_access_token_env=int(os.getenv("EXPIRATION_ACCESS_TOKEN"))
exp_refresh_token_env=int(os.getenv("EXPIRATION_REFRESH_TOKEN"))

http_only_env=bool(os.getenv("HTTPONLY"))
secure_env=bool(os.getenv("SECURE"))
samesite_env=os.getenv("SAMESITE")