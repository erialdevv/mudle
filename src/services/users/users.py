import logging
import re
import uuid
from core.general.errors import BadRequestError, ConflictError, FieldValidationError, NotFoundError
from core.security.password import hash_password
from core.general.pagination import build_page
from repositories.users.users import repo_get_all_users, repo_insert_user, repo_update_user, repo_get_user_by_code, repo_canceled_user_by_id
from models.users.users import User

logger = logging.getLogger(__name__)

_FIELD_MAP = {
    "EMAIL": "institutional_email",
    "FIRST_NAME": "first_name",
    "LAST_NAME": "last_name",
}


def _build_user(**kwargs) -> User:
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


async def _fetch_user(conn, user_code: uuid.UUID | str) -> dict:
    """Consulta el usuario por su código (UUID); si no existe lanza NotFoundError (404).
    El ID interno nunca viaja por la API: se obtiene aquí y solo se usa hacia la BD."""
    result: dict = await repo_get_user_by_code(conn, p_codigo=uuid.UUID(str(user_code)))
    if result["data"] is None:
        raise NotFoundError("El usuario solicitado no existe.")
    return result


async def service_update_user(conn, allowed_domains, **data) -> dict:
    password = data.get("password")

    user = _build_user(
        code=data.get("code"),
        edited_by=data.get("edited_by"),
        pcid=data.get("pcid"),
        password=hash_password(password) if password else None,
        email=data.get("institutional_email"),
        allowed_domains=allowed_domains if data.get("institutional_email") else None,
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
    )

    current: dict = (await _fetch_user(conn, user.code))["data"]

    #validacion de logica booleana para ver si almenos uno de esos tienen un cambio
    has_changes = (
        user.password is not None
        or (user.first_name is not None and user.first_name != current["first_name"])
        or (user.last_name is not None and user.last_name != current["last_name"])
        or (user.email is not None and user.email != current["institutional_email"])
    )
    if not has_changes:
        raise BadRequestError("No se realizaron cambios porque los datos enviados son iguales a los actuales.")

    sp_parameters: dict = {
        "p_id": current["id"],
        "p_editado_por": user.edited_by,
        "p_nombre": user.first_name,
        "p_apellido": user.last_name,
        "p_email_est": user.email,
        "p_contrasena": user.password
    }

    return await repo_update_user(conn, **sp_parameters)


async def service_get_user(conn, **data) -> dict:
    result: dict = await _fetch_user(conn, data["p_codigo"])

    return {
        "msg": result["msg"],
        "detail": {"data_user": result["data"]},
    }


async def service_get_all_users(conn, page: int, limit: int, search: str | None, only_active: bool) -> dict:
    result: dict = await repo_get_all_users(
        conn,
        p_limit=limit,
        p_offset=(page - 1) * limit,
        p_search=search,
        p_only_active=only_active,
    )
    items, pagination = build_page(result["data"], page, limit)

    return {"msg": result["msg"], "detail": items, "pagination": pagination}


async def service_canceled_user(conn, **data) -> dict:
    current: dict = (await _fetch_user(conn, data["p_codigo"]))["data"]

    if current["voided"]:
        raise ConflictError("El usuario ya se encuentra anulado.")

    await repo_canceled_user_by_id(conn, p_id=current["id"], p_editado_por=data["p_editado_por"])

    return {"msg": "Usuario anulado exitosamente."}
