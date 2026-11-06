import re
from sqlalchemy.ext.asyncio import create_async_engine
from db.config import database_url

#import asyncio

#obtencion de la url de la bd
db_url = re.sub(
    r'^postgresql:',
    'postgresql+psycopg:',
    database_url
)

engine = create_async_engine(db_url, echo=True,pool_pre_ping=True)

