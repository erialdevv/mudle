from fastapi import APIRouter

from routers.general.util import router as utilities
from routers.users.users import router as users
from routers.auth.login import router as login
from routers.roles.role import router as roles

router=APIRouter()

router.include_router(utilities)
router.include_router(users)
router.include_router(login)
router.include_router(roles)