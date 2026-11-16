from repositories.general.startup import get_domains
from db.connection import engine
import asyncio
from fastapi import FastAPI

async def data_load_task(app: FastAPI, interval_seconds: int):
    while True:
        try:
            await asyncio.sleep(interval_seconds)

            domains = await get_domains(engine)

            if not domains["status"]:
                print(
                    f"Error al consultar los dominios: {domains['msg']}. "
                    "Reintentando en 15 segundos..."
                )
                await asyncio.sleep(15)
                continue

            app.state.allowed_domains = set(domains["result"])

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

