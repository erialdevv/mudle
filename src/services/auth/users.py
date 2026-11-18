import logging
import re
from core.security.password import hash_password
from repositories.auth.users import repo_insert_user, repo_update_user, repo_get_user_by_id
from models.auth.users import User

logger = logging.getLogger(__name__)
INTERNAL_MSG = "Ocurrió un error interno al procesar la solicitud."

_FIELD_MAP = {
    "EMAIL": "institutional_email",
    "FIRST_NAME": "first_name",
    "LAST_NAME": "last_name",
}

def _validation_error(val_error: ValueError) -> dict:
    """Errores de campo del modelo (`[EMAIL]: ...`) -> 422; cualquier otro ValueError -> 400."""
    message = str(val_error)
    match = re.match(r"^\[(\w+)\]:\s*(.*)$", message)
    if match and match.group(1) in _FIELD_MAP:
        return {
            "status": False,
            "status_code": 422,
            "field": _FIELD_MAP[match.group(1)],
            "msg": match.group(2),
        }
    return {"status": False, "status_code": 400, "msg": message}

async def service_save_user(conn, allowed_domains, **data) -> dict:
    try:
        password_hash = hash_password(data["password"])

        domain_user = User(
            created_by=data.get("created_by"),
            pcid=data.get("pcid"),
            password=password_hash,
            email=data["institutional_email"],
            allowed_domains=allowed_domains,
            first_name=data["first_name"],
            last_name=data["last_name"]
        )

        sp_parameters: dict = {
            "p_contrasena": domain_user.password,
            "p_email_est": domain_user.email,
            "p_creado_por": domain_user.created_by,
            "p_pcid": domain_user.pcid,
            "p_nombre": domain_user.first_name,
            "p_apellido": domain_user.last_name
        }

        # 4xx/5xx: Error devuelto por el procedimiento almacenado
        save_result: dict = await repo_insert_user(conn, **sp_parameters)
        if not save_result["status"]:
            return {
                "status": False,
                "status_code": save_result.get("status_code", 400),
                "msg": save_result["msg"]
            }

        return {"status": True, "msg": save_result["msg"]}

    except ValueError as val_error:
        return _validation_error(val_error)
    except Exception:
        logger.exception("Error inesperado al crear el usuario")
        return {"status": False, "status_code": 500, "msg": INTERNAL_MSG}

async def service_update_user(conn, allowed_domains, **data) -> dict:
    try:
        password = data.get("password")
        password_hash = hash_password(password) if password else None

        user = User(
            id=data.get("id"),
            edited_by=data.get("edited_by"),
            pcid=data.get("pcid"),
            password=password_hash,
            email=data.get("institutional_email"),
            allowed_domains=allowed_domains if data.get("institutional_email") else None,
            first_name=data.get("first_name"),
            last_name=data.get("last_name")
        )

        sp_parameters: dict = {
            "p_id": int(user.id),
            "p_editado_por": user.edited_by,
            "p_nombre": user.first_name,
            "p_apellido": user.last_name,
            "p_email_est": user.email,
            "p_contrasena": user.password
        }

        # 4xx/5xx: Error devuelto por el procedimiento almacenado
        update_result: dict = await repo_update_user(conn, **sp_parameters)
        if not update_result["status"]:
            return {
                "status": False,
                "status_code": update_result.get("status_code", 400),
                "msg": update_result["msg"]
            }

        return {"status": True, "msg": update_result["msg"]}

    except ValueError as val_error:
        return _validation_error(val_error)
    except Exception:
        logger.exception("Error inesperado al actualizar el usuario")
        return {"status": False, "status_code": 500, "msg": INTERNAL_MSG}

async def service_get_user(conn,**data):
    try:
        
        result:dict=await repo_get_user_by_id(conn,**data)
        
        if not result:
            return result
        
        return{
            "status":True,
            "msg":result["msg"],
            "detail":{
                "data_user":result["data"]
            }
        }
        
    except ValueError as val_error:
            return _validation_error(val_error)
    except Exception:
            logger.exception("Error inesperado al crear el usuario")
            return {"status": False, "status_code": 500, "msg": INTERNAL_MSG}

