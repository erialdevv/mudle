from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException,status
from db.connection import engine
from db.config import tiempo_refresco
from repositories.general.arranque import obtener_dominios
import asyncio
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.general.util import  tarea_carga_datos
from routers import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.dominios_permitidos = set()
    tarea_background = None
    
    try:
        dominios = await obtener_dominios(engine)
        if not dominios["estado"]:
            raise RuntimeError(
                f"No se pudieron cargar los dominios permitidos: {dominios['msg']}"
            )
            
        app.state.dominios_permitidos = set(dominios["resultado"])
        tarea_background = asyncio.create_task(
            tarea_carga_datos(app,tiempo_segundos=tiempo_refresco)
        )
        
        yield
        
    except Exception as error:
        app.state.dominios_permitidos=None
        print(f"Fallo en el ciclo de vida: {type(error).__name__}: {error}")
        raise
    finally:
        if tarea_background:
            tarea_background.cancel()
            await asyncio.gather(tarea_background, return_exceptions=True)
        
        await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(router)



