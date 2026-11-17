import re
from sqlalchemy.ext.asyncio import create_async_engine
from db.config import DBConfig

#import asyncio

#obtencion de la url de la bd
db_url = re.sub(
    r'^postgresql:',
    'postgresql+psycopg:',
    DBConfig.database_url
)

engine = create_async_engine(db_url, echo=True,pool_pre_ping=True)

