from contextlib import asynccontextmanager
from fastapi import FastAPI
from db.connection import engine
from db.config import DBConfig
from repositories.general.startup import get_domains
import asyncio
from core.general.util import  data_load_task
from routers import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.allowed_domains = set()
    background_task = None
    
    try:
        domains = await get_domains(engine)
        if not domains["status"]:
            raise RuntimeError(
                f"No se pudieron cargar los dominios permitidos: {domains['msg']}"
            )
            
        app.state.allowed_domains = set(domains["result"])
        background_task = asyncio.create_task(
            data_load_task(app,interval_seconds=DBConfig.refresh_interval)
        )
        
        yield
        
    except Exception as error:
        app.state.allowed_domains=None
        print(f"Fallo en el ciclo de vida de la aplicación: {type(error).__name__}: {error}")
        raise
    finally:
        if background_task:
            background_task.cancel()
            await asyncio.gather(background_task, return_exceptions=True)
        
        await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(router)
