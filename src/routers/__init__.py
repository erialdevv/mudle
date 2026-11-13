from fastapi import APIRouter

from routers.general.util import router as utilities
from routers.auth.users import router as users
from routers.auth.login import router as login

router=APIRouter()

router.include_router(utilities)
router.include_router(users)
router.include_router(login)

