from models.roles.role import Role
import re
from core.general.errors import BadRequestError, ConflictError, FieldValidationError, NotFoundError
from core.general.pagination import build_page
from repositories.roles.roles import repo_insert_roles, repo_get_roles, repo_get_all_roles

_FIELD_MAP = {
    "NAME": "p_nombre",
    "VERSION": "p_version",
}


def _build_role(**kwargs) -> Role:
    """Construye el modelo de dominio. Sus ValueError se traducen a errores de la app:
    `[EMAIL]: ...` -> 422 con el campo; cualquier otro ValueError -> 400."""
    try:
        return Role(**kwargs)
    except ValueError as val_error:
        message = str(val_error)
        match = re.match(r"^\[(\w+)\]:\s*(.*)$", message)
        if match and match.group(1) in _FIELD_MAP:
            raise FieldValidationError(match.group(2), field=_FIELD_MAP[match.group(1)]) from val_error
        raise BadRequestError(message) from val_error


async def service_save_roles(
    conn,
    **data
):
    domain_role=_build_role(
        created_by=data.get("created_by"),
        pcid=data.get("pcid"),
        name=data["p_nombre"],
        version=data["p_version"],
        permissions=data["p_permissions"]
    )
    
    sp_parameters:dict={
        "p_nombre":domain_role.name,
        "p_version":domain_role.version,
        "p_permissions":domain_role.permissions,
        "p_created_by":domain_role.created_by,
        "p_pcid":domain_role.pcid
    }
    
    return await repo_insert_roles(conn,**sp_parameters)
    
async def service_get_roles(conn,role_id:int):
    
    sp_parameters:dict={
        "p_rol_id":role_id
    }
    
    result:dict=await repo_get_roles(conn, **sp_parameters)
    data:dict|None=result["data"]

    if data is None:
        raise NotFoundError(f"El rol del usuario en sesion no existe.")
    
    return{
        "msg":result["msg"],
        "detail":data
    }
        
async def service_get_all_roles(conn, page: int, limit: int, search: str | None, only_active: bool):
    sp_parameters: dict = {
        "p_limit": limit,
        "p_offset": (page - 1) * limit,
        "p_search": search,
        "p_only_active": only_active,
    }

    result: dict = await repo_get_all_roles(conn, **sp_parameters)
    items, pagination = build_page(result["data"], page, limit)

    return {"msg": result["msg"], "detail": items, "pagination": pagination}
