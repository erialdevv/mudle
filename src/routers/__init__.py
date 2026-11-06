from fastapi import APIRouter

from routers.general.util import router as utilidades

router=APIRouter()

router.include_router(utilidades)
