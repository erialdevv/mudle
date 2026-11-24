from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from db.connection import engine
from db.config import DBConfig
from repositories.general.startup import get_domains
import asyncio
from core.general.util import  data_load_task
from routers import router
from core.general.errors import AppError
from db.redis_client import redis_client

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.allowed_domains = set()
    background_task = None
    
    try:
        #validacion de redis
        await redis_client.ping()
        
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
        
        await redis_client.aclose()
        
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


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    """traduccion de los errores controlados de la app a HTTP"""
    if exc.field:
        detail = [{"loc": ["body", exc.field], "msg": exc.msg, "type": "value_error"}]
    else:
        detail = exc.msg
    return JSONResponse(status_code=exc.status_code, content={"detail": detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Manejador global: cualquier error no controlado responde 500 y se registra"""
    logger.error(
        "Error inesperado en %s %s", request.method, request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Ocurrió un error interno al procesar la solicitud."},
    )
