from fastapi import APIRouter, status, Response, Depends
from schemas.roles.responses import RoleRequest
from schemas.general.responses import error_responses
from repositories.general.util import DB_ERROR_CODES
from schemas.general.responses import BaseResponse
from schemas.roles.responses import RoleReadResponse
from db.connection import DbConn
from core.permissions.service_permissions import validate_permissions
from core.permissions.bitmask_engine import SystemModules, ActionsPermissions
from services.roles.roles import service_save_roles, service_get_roles

router=APIRouter(
    prefix="/role",
    tags=["Roles"],
    responses=error_responses(401)
)



@router.post(
    "/create",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
    summary="Creacion de roles",
    responses=error_responses(*DB_ERROR_CODES),
)
async def router_insert_role(
    body: RoleRequest,
    conn: DbConn,
    token_data: dict = Depends(validate_permissions(SystemModules.ROLES, ActionsPermissions.PERM_CREATE))
):
    data: dict = body.model_dump()
    data["created_by"] = token_data["code"]
    data["pcid"] = token_data["pcid"]
    
    result=await service_save_roles(conn,**data)
    
    return{"status":True, "msg":result["msg"]}
    

@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=RoleReadResponse,
    summary="Ver roles",
    responses=error_responses(*DB_ERROR_CODES),
)
async def router_get_role_me(
    conn: DbConn,
    token_data: dict = Depends(validate_permissions(SystemModules.ROLES, ActionsPermissions.PERM_READ))
):
    role_id:int=token_data.get("rol_id")
    
    result:dict=await service_get_roles(conn,role_id)
    detail:dict=result["detail"]
    
    return{
        "status":True,
        "msg":result["msg"],
        "detail":{
            "code":detail.get("codigo"),
            "name":detail.get("nombre"),
            "version":detail.get("version"),
            "permissions":detail.get("permissions"),
            "voided":detail.get("anulado")
        }
    }