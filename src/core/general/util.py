from repositories.general.arranque import obtener_dominios
from db.connection import engine
import asyncio
from fastapi import FastAPI

DOMINIOS_PERMITIDOS=set()

async def tarea_carga_datos(app:FastAPI,tiempo_segundos:int):
    
    global DOMINIOS_PERMITIDOS
    
    while True:
        try:
            dominios = await obtener_dominios(engine)

            if not dominios["estado"]:
                print(
                    f"Error al consultar los dominios: {dominios['msg']}. "
                    "Reintentando en 15 segundos..."
                )
                await asyncio.sleep(15)
                continue

            app.state.dominios_permitidos= set(dominios["resultado"])

            await asyncio.sleep(tiempo_segundos)

        except asyncio.CancelledError:
            print("Temporizador detenido.")
            raise

        except Exception as error:
            print(
                f"Error inesperado al actualizar los dominios: "
                f"{type(error).__name__}: {error}. "
                "Reintentando en 15 segundos..."
            )
            await asyncio.sleep(15)