from fastapi import APIRouter, HTTPException, status, Request, Path, Depends
from schemas.auth.users import CreateUserRequest, ReadUserResponse, UpdateUserRequest
from services.auth.users import service_update_user, service_save_user
from db.connection import engine
import uuid
from core.security.token import get_current_user

router=APIRouter(
    prefix="/users",
    tags=["Users"],
)

@router.post("",status_code=status.HTTP_201_CREATED)
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
    
    
    
@router.get("/me", status_code=status.HTTP_200_OK)
async def router_get_user(
):
    pass



@router.patch("/update/{id}",summary="Actualizar usuario",status_code=status.HTTP_200_OK)
async def router_update_user(
    request_http:Request,
    body:UpdateUserRequest=...,
    id:str=Path(...,description="id  del usuario para editar"),
    datos_log:dict=Depends(get_current_user)
):
    try:
        async with engine.begin() as conn:
            
            data: dict = body.model_dump(exclude_unset=True)
            
            #Ingreso de claves a datos por necesidad en desarrollo, en produccion estos datos se
            #reciben por la url
            data["id"]=id
            data["edited_by"]=datos_log["code"]
            data["pcid"]=datos_log["pcid"]
            
    
            
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
