from fastapi import APIRouter, HTTPException, status, Request
from db.connection import engine
from schemas.auth.login import LoginRequest
from services.auth.login import service_login

router=APIRouter(
    prefix="/login",
    tags=["Login"],
)

@router.post("/login",status_code=status.HTTP_201_CREATED)
async def router_login(request:LoginRequest):
    try:
        async with engine.begin() as conn:
            data:dict=request.model_dump()

            return await service_login(conn, **data)
            
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=str(error))
