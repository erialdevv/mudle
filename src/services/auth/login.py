import logging
from core.general.errors import UnauthorizedError, InternalError
from core.security.password import verify_password
from core.security.token import create_access_token, create_refresh_token
from repositories.auth.login import repo_valid_login, repo_insert_refresh_token, repo_validar_refresh_token, repo_logout

logger = logging.getLogger(__name__)

INVALID_CREDENTIALS_MSG = "Correo o contraseña incorrectos."


async def service_login(conn, **data) -> dict:
    email: str = data["email"]
    password: str = data["password"]

    user_valid: dict | None = await repo_valid_login(conn, email)

    # 401: mismo mensaje para usuario inexistente y clave errónea, evita enumerar usuarios
    if not user_valid:
        raise UnauthorizedError(INVALID_CREDENTIALS_MSG)

    # 500: fallo interno de integridad en BD
    if not user_valid.get("password"):
        logger.error("Usuario %s sin contraseña registrada", user_valid.get("id"))
        raise InternalError("Error interno en la configuración del usuario.")

    if not verify_password(password, user_valid["password"])["status"]:
        raise UnauthorizedError(INVALID_CREDENTIALS_MSG)

    # 500: error al firmar los JWT (el detalle va al log, no al cliente)
    access_result: dict = create_access_token(user_valid["id"], user_valid["code"], user_valid["first_name"])
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
    # Si el SP rechaza el token (revocado/expirado/no registrado) lanza ERRCODE 'TT401' -> 401
    sp_result: dict = await repo_validar_refresh_token(
        conn,
        p_jti=data["jti"],
        p_user_code=data["code"],
        p_pcid=data["pcid"],
    )

    access_result: dict = create_access_token(data["id"], data["code"], data["pcid"])
    if not access_result["status"]:
        logger.error(access_result["msg"])
        raise InternalError("No se pudo generar el token de acceso.")

    return {
        "msg": f"{sp_result['msg']}, y se generó correctamente el nuevo token de acceso",
        "detail": {"access_token": access_result["detail"]["token"]}
    }

async def service_logout(conn, **data) -> dict:
    await repo_logout(conn, p_jti=data["jti"], p_user_code=data["code"])
    return {"msg": "Sesión cerrada exitosamente."}
