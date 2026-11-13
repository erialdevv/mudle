from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException,status
from db.connection import engine
from db.config import refresh_interval
from repositories.general.startup import get_domains
import asyncio
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
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
                f"Could not load the allowed domains: {domains['msg']}"
            )
            
        app.state.allowed_domains = set(domains["result"])
        background_task = asyncio.create_task(
            data_load_task(app,interval_seconds=refresh_interval)
        )
        
        yield
        
    except Exception as error:
        app.state.allowed_domains=None
        print(f"Lifespan failure: {type(error).__name__}: {error}")
        raise
    finally:
        if background_task:
            background_task.cancel()
            await asyncio.gather(background_task, return_exceptions=True)
        
        await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(router)
