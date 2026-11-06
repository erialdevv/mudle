import os
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL")
tiempo_refresco = int(os.getenv("TASA_REFRESCO_DATOS", "60")) * 60