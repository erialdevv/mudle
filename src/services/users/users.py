import logging
import re
from core.general.errors import BadRequestError, FieldValidationError
from core.security.password import hash_password
from repositories.users.users import repo_insert_user, repo_update_user, repo_get_user_by_id, repo_canceled_user_by_id
from models.users.users import User

logger = logging.getLogger(__name__)

_FIELD_MAP = {
    "EMAIL": "institutional_email",
    "FIRST_NAME": "first_name",
    "LAST_NAME": "last_name",
}


def _build_user(**kwargs) -> User:
    """Construye el modelo de dominio. Sus ValueError se traducen a errores de la app:
    `[EMAIL]: ...` -> 422 con el campo; cualquier otro ValueError -> 400."""
    try:
        return User(**kwargs)
    except ValueError as val_error:
        message = str(val_error)
        match = re.match(r"^\[(\w+)\]:\s*(.*)$", message)
        if match and match.group(1) in _FIELD_MAP:
            raise FieldValidationError(match.group(2), field=_FIELD_MAP[match.group(1)]) from val_error
        raise BadRequestError(message) from val_error


async def service_save_user(conn, allowed_domains, **data) -> dict:
    domain_user = _build_user(
        created_by=data.get("created_by"),
        pcid=data.get("pcid"),
        password=hash_password(data["password"]),
        email=data["institutional_email"],
        allowed_domains=allowed_domains,
        first_name=data["first_name"],
        last_name=data["last_name"],
    )

    sp_parameters: dict = {
        "p_contrasena": domain_user.password,
        "p_email_est": domain_user.email,
        "p_creado_por": domain_user.created_by,
        "p_pcid": domain_user.pcid,
        "p_nombre": domain_user.first_name,
        "p_apellido": domain_user.last_name
    }

    return await repo_insert_user(conn, **sp_parameters)


async def service_update_user(conn, allowed_domains, **data) -> dict:
    password = data.get("password")

    user = _build_user(
        user_id=data.get("id"),
        edited_by=data.get("edited_by"),
        pcid=data.get("pcid"),
        password=hash_password(password) if password else None,
        email=data.get("institutional_email"),
        allowed_domains=allowed_domains if data.get("institutional_email") else None,
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
    )

    sp_parameters: dict = {
        "p_id": int(user.id),
        "p_editado_por": user.edited_by,
        "p_nombre": user.first_name,
        "p_apellido": user.last_name,
        "p_email_est": user.email,
        "p_contrasena": user.password
    }

    return await repo_update_user(conn, **sp_parameters)


async def service_get_user(conn, **data) -> dict:
    result: dict = await repo_get_user_by_id(conn, **data)

    return {
        "msg": result["msg"],
        "detail": {"data_user": result["data"]},
    }


async def service_canceled_user(conn, **data) -> dict:
    await repo_canceled_user_by_id(conn, **data)

    return {"msg": "Usuario anulado exitosamente."}
