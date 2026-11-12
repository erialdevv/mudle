from repositories.general.arranque import obtener_dominios
from db.connection import engine
import asyncio
from fastapi import FastAPI

async def tarea_carga_datos(app: FastAPI, tiempo_segundos: int):
    while True:
        try:
            await asyncio.sleep(tiempo_segundos)

            dominios = await obtener_dominios(engine)

            if not dominios["estado"]:
                print(
                    f"Error al consultar los dominios: {dominios['msg']}. "
                    "Reintentando en 15 segundos..."
                )
                await asyncio.sleep(15)
                continue

            app.state.dominios_permitidos = set(dominios["resultado"])

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
