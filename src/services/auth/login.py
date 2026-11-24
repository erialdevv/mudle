import logging
from core.general.errors import UnauthorizedError, InternalError
from core.security.password import verify_password
from core.security.token import create_access_token, create_refresh_token
from repositories.auth.login import repo_valid_login, repo_insert_refresh_token, repo_get_refresh_session, repo_logout
from core.permissions.permission_cache import get_role_permissions
from db.redis_client import redis_client

logger = logging.getLogger(__name__)

INVALID_CREDENTIALS_MSG = "Correo o contraseña incorrectos."


async def service_login(conn, **data) -> dict:
    email: str = data["email"]
    password: str = data["password"]

    user_valid: dict | None = await repo_valid_login(conn, email)

    if not user_valid:
        raise UnauthorizedError(INVALID_CREDENTIALS_MSG)

    if not user_valid.get("password"):
        logger.error("Usuario %s sin contraseña registrada", user_valid.get("id"))
        raise InternalError("Error interno en la configuración del usuario.")

    if not verify_password(password, user_valid["password"])["status"]:
        raise UnauthorizedError(INVALID_CREDENTIALS_MSG)


    perm_data:dict=await get_role_permissions(redis_client,conn,user_valid["roleid"])

    access_result: dict = create_access_token(
        user_valid["id"], 
        user_valid["code"],
        user_valid["roleid"],
        perm_data["vers_rol"],
        #Aqui en este parametro se encuentran 
        # los permisos en formato de diccionario que al payload del token pasan como str
        perm_data["mask_bits"],
        user_valid["first_name"]
    )
    
    if not access_result["status"]:
        logger.error(access_result["msg"])
        raise InternalError("No se pudo generar el token de acceso.")

    refresh_result: dict = create_refresh_token(user_valid["id"], user_valid["code"], user_valid["first_name"])
    if not refresh_result["status"]:
        logger.error(refresh_result["msg"])
        raise InternalError("No se pudo generar el token de refresco.")

    refresh_data = refresh_result["detail"]

    await repo_insert_refresh_token(
        conn,
        p_id=refresh_data["token_id"],
        p_usuario_id=user_valid["id"],
        p_fecha_expiracion=refresh_data["exp"],
        p_pcid=user_valid["first_name"],
    )

    return {
        "msg": "Inicio de sesión completado exitosamente.",
        "detail": {
            "user_id": user_valid["id"],
            "access_token": access_result["detail"]["token"],
            "refresh_token": refresh_data["token"],
            "refresh_token_exp": refresh_data["exp"]
        }
    }

async def service_validate_token(conn, **data) -> dict:
    
    session: dict | None = await repo_get_refresh_session(conn, data["jti"], data["code"])

    # Reglas de validez de la sesión (todas son 401)
    if session is None:
        raise UnauthorizedError("Token de actualización no encontrado o inválido.")
    if session["usuario_anulado"]:
        raise UnauthorizedError("La cuenta de usuario se encuentra inactiva o anulada.")
    if session["token_anulado"]:
        raise UnauthorizedError("La sesión ha sido revocada.")
    if session["expirado"]:
        raise UnauthorizedError("El refresh token ha expirado.")
    if session["pcid"] != data["pcid"]:
        raise UnauthorizedError("El identificador de sesión no coincide.")

    # Los permisos se leen de nuevo (caché/BD) para reflejar cambios del rol desde el login
    perm_data: dict = await get_role_permissions(redis_client, conn, session["roleid"])

    access_result: dict = create_access_token(
        data["id"],
        data["code"],
        session["roleid"],
        perm_data["vers_rol"],
        perm_data["mask_bits"],
        data["pcid"],
    )
    if not access_result["status"]:
        logger.error(access_result["msg"])
        raise InternalError("No se pudo generar el token de acceso.")

    return {
        "msg": "Token de refresco validado correctamente, y se generó correctamente el nuevo token de acceso",
        "detail": {"access_token": access_result["detail"]["token"]}
    }

async def service_logout(conn, **data) -> dict:
    # Idempotente: si la sesión ya estaba revocada, el objetivo (sesión cerrada) ya se cumplió
    await repo_logout(conn, p_jti=data["jti"], p_user_code=data["code"])
    return {"msg": "Sesión cerrada exitosamente."}
