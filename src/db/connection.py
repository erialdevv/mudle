import re
from collections.abc import AsyncIterator
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine
from db.config import DBConfig

#import asyncio

#obtencion de la url de la bd
db_url = re.sub(
    r'^postgresql:',
    'postgresql+psycopg:',
    DBConfig.database_url
)

engine = create_async_engine(db_url, echo=True,pool_pre_ping=True)


async def get_db() -> AsyncIterator[AsyncConnection]:
    """Abre una conexión con transacción por petición.

    Commit automático si el endpoint termina bien; rollback si lanza cualquier excepción.
    """
    async with engine.begin() as conn:
        yield conn


# scope="function": el commit/rollback ocurre al terminar el endpoint y ANTES de enviar la respuesta.
# Sin esto, el commit se haría después de responder y el cliente podría leer datos aún no confirmados.
# FastAPI cachea la dependencia por petición: todo lo que la use comparte la misma conexión/transacción.
DbConn = Annotated[AsyncConnection, Depends(get_db, scope="function")]
