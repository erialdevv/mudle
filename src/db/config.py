import os
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL")
tiempo_refresco = int(os.getenv("TASA_REFRESCO_DATOS", "60")) * 60
time_cost_env=int(os.getenv("TIME_COST"))
memory_cost_env=int(os.getenv("MEMORY_COST"))
parallelism_env=int(os.getenv("PARALLELISM"))