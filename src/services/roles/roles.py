from models.roles.role import Role
import re
from core.general.errors import BadRequestError, ConflictError, FieldValidationError, NotFoundError
from repositories.roles.roles import repo_insert_roles

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
    
    