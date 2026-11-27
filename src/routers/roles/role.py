from fastapi import APIRouter, status, Depends, Query, Path
import uuid
from typing import Optional
from schemas.roles.responses import RoleRequest
from schemas.general.responses import error_responses
from repositories.general.util import DB_ERROR_CODES
from schemas.general.responses import BaseResponse
from schemas.roles.responses import RoleReadResponse, RoleListResponse
from db.connection import DbConn
from core.permissions.service_permissions import validate_permissions
from core.permissions.bitmask_engine import SystemModules, ActionsPermissions
from services.roles.roles import (
    service_save_roles, 
    service_get_roles_me, 
    service_get_all_roles, 
    service_get_roles
)
router=APIRouter(
    prefix="/role",
    tags=["Roles"],
    responses=error_responses(401)
)

@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
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
    summary="Obtener roles de usuario autenticado",
    responses=error_responses(*DB_ERROR_CODES),
)
async def router_get_role_me(
    conn: DbConn,
    token_data: dict = Depends(validate_permissions(SystemModules.ROLES, ActionsPermissions.PERM_READ))
):
    role_id:int=token_data.get("rol_id")
    
    result:dict=await service_get_roles_me(conn,role_id)

    return {"status":True,"msg":result["msg"],"detail":result["detail"]}

@router.get(
    "/all",
    status_code=status.HTTP_200_OK,
    response_model=RoleListResponse,
    summary="Obtener todos los roles creados",
    responses=error_responses(*DB_ERROR_CODES),
)
async def router_get_all_roles(
    conn: DbConn,
    page: int = Query(1, ge=1, description="Página actual"),
    limit: int = Query(10, ge=1, le=100, description="Cantidad de registros por página"),
    search: Optional[str] = Query(None, description="Texto para buscar por nombre"),
    only_active: bool = Query(True, description="Si es True trae solo los no anulados"),
    token_data: dict = Depends(validate_permissions(SystemModules.ROLES, ActionsPermissions.PERM_READ))
):
    result: dict = await service_get_all_roles(conn, page, limit, search, only_active)

    return {"status": True, **result}

@router.get(
    "/{user_code}",
    response_model=RoleReadResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener rol de usuario por código",
    responses=error_responses(*DB_ERROR_CODES)
)
async def router_get_role_user(
    conn:DbConn,
    user_code: uuid.UUID = Path(..., description="Código (UUID) del usuario a consultar"),
    token_data: dict = Depends(validate_permissions(SystemModules.ROLES, ActionsPermissions.PERM_READ))
):
    result:dict=await service_get_roles(conn,user_code=user_code)
    
    return {"status":True,"msg":result["msg"],"detail":result["detail"]}