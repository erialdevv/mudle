from fastapi import APIRouter

from routers.general.util import router as utilidades
from routers.auth.usuarios import router as usuarios

router=APIRouter()

router.include_router(utilidades)
router.include_router(usuarios)
