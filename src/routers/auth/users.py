from fastapi import APIRouter, HTTPException, status, Request
from schemas.auth.users import CreateUserRequest, ReadUserResponse, UpdateUserRequest
from services.auth.users import service_update_user, service_save_user
from db.connection import engine
import uuid

router=APIRouter(
    prefix="/users",
    tags=["Users"],
)

@router.post("/register",status_code=status.HTTP_201_CREATED)
async def router_insert_user(
    request:CreateUserRequest,
    request_http:Request
):
    try:
        async with engine.begin() as conn:
            data=request.model_dump()
            
            data["created_by"]=uuid.UUID("157485ce-de04-4c0a-8606-fddf9ed5a3e8")
            data["pcid"]="Administrador"
            
            domains=list(request_http.app.state.allowed_domains)
            
            result=await service_save_user(conn ,domains,**data)
   
            if not result["status"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["msg"])
            
            return result
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

@router.patch("/update",status_code=status.HTTP_200_OK)
async def router_update_user(
    request:UpdateUserRequest,
    request_http:Request
):
    try:
        async with engine.begin() as conn:
            
            data: dict = request.model_dump(exclude_unset=True)
            
            #Ingreso de claves a datos por necesidad en desarrollo, en produccion estos datos se
            #reciben por el header
            data["edited_by"]=uuid.UUID("157485ce-de04-4c0a-8606-fddf9ed5a3e8")
            data["pcid"]="Administrador"
            
            domains=None
            if data.get("institutional_email"):
                domains=list(request_http.app.state.allowed_domains)
          
            result=await service_update_user(conn,domains,**data)
            
            if not result["status"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["msg"])
            
            
            return result
                 
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=str(error))
