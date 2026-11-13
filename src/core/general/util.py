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
                    f"Error querying domains: {domains['msg']}. "
                    "Retrying in 15 seconds..."
                )
                await asyncio.sleep(15)
                continue

            app.state.allowed_domains = set(domains["result"])

        except asyncio.CancelledError:
            print("Timer stopped.")
            raise

        except Exception as error:
            print(
                f"Unexpected error while updating domains: "
                f"{type(error).__name__}: {error}. "
                "Retrying in 15 seconds..."
            )
            await asyncio.sleep(15)

