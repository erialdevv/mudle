import logging
from core.security.password import verify_password
from core.security.token import create_access_token, create_refresh_token
from repositories.auth.login import repo_valid_login, repo_insert_refresh_token, repo_validar_refresh_token, repo_logout

logger = logging.getLogger(__name__)

INTERNAL_MSG = "Ocurrió un error interno al procesar la solicitud."
INVALID_CREDENTIALS_MSG = "Correo o contraseña incorrectos."

async def service_login(conn, **data) -> dict:
    try:
        email: str = data["email"]
        password: str = data["password"]

        user_valid: dict | None = await repo_valid_login(conn, email)

        # 401: Credenciales inválidas (mismo mensaje para usuario inexistente y clave errónea, evita enumerar usuarios)
        if not user_valid:
            return {"status": False, "status_code": 401, "msg": INVALID_CREDENTIALS_MSG}

        # 500: Fallo interno de integridad en BD
        if not user_valid.get("password"):
            logger.error("Usuario %s sin contraseña registrada", user_valid.get("id"))
            return {"status": False, "status_code": 500, "msg": "Error interno en la configuración del usuario."}

        # 401: La contraseña no coincide
        password_result: dict = verify_password(password, user_valid["password"])
        if not password_result["status"]:
            return {"status": False, "status_code": 401, "msg": INVALID_CREDENTIALS_MSG}

        # 500: Error interno al firmar los JWT (el detalle va al log, no al cliente)
        access_result: dict = create_access_token(user_valid["id"], user_valid["code"], user_valid["first_name"])
        if not access_result["status"]:
            logger.error(access_result["msg"])
            return {"status": False, "status_code": 500, "msg": "No se pudo generar el token de acceso."}

        refresh_result: dict = create_refresh_token(user_valid["id"], user_valid["code"], user_valid["first_name"])
        if not refresh_result["status"]:
            logger.error(refresh_result["msg"])
            return {"status": False, "status_code": 500, "msg": "No se pudo generar el token de refresco."}

        access_token = access_result["detail"]["token"]
        refresh_data = refresh_result["detail"]

        sp_parameters: dict = {
            "p_id": refresh_data["token_id"],
            "p_usuario_id": user_valid["id"],
            "p_fecha_expiracion": refresh_data["exp"],
            "p_pcid": user_valid["first_name"]
        }

        # Error al guardar el refresh token (500 o 503 si la BD no está disponible)
        save_result: dict = await repo_insert_refresh_token(conn, **sp_parameters)
        if not save_result["status"]:
            return {
                "status": False,
                "status_code": 503 if save_result.get("status_code") == 503 else 500,
                "msg": save_result["msg"]
            }

        return {
            "status": True,
            "msg": "Inicio de sesión completado exitosamente.",
            "detail": {
                "user_id": user_valid["id"],
                "access_token": access_token,
                "refresh_token": refresh_data["token"],
                "refresh_token_exp": refresh_data["exp"]
            }
        }

    except ValueError as val_error:
        return {"status": False, "status_code": 400, "msg": str(val_error)}
    except Exception:
        logger.exception("Error inesperado en el inicio de sesión")
        return {"status": False, "status_code": 500, "msg": INTERNAL_MSG}

async def service_validate_token(conn, **data) -> dict:
    try:
        sp_parameters: dict = {
            "p_jti": data["jti"],
            "p_user_code": data["code"],
            "p_pcid": data["pcid"]
        }

        lcsql_result: dict = await repo_validar_refresh_token(conn, **sp_parameters)
        if not lcsql_result["status"]:
            # Rechazo del SP (token revocado/expirado/no registrado) -> 401; fallos de infraestructura conservan su código
            sp_status = lcsql_result.get("status_code", 401)
            status_code = sp_status if sp_status in (500, 503) else 401
            return {"status": False, "status_code": status_code, "msg": lcsql_result["msg"]}

        access_result: dict = create_access_token(data["id"], data["code"], data["pcid"])
        if not access_result["status"]:
            logger.error(access_result["msg"])
            return {"status": False, "status_code": 500, "msg": "No se pudo generar el token de acceso."}

        access_token = access_result["detail"]["token"]

        return {
            "status": True,
            "msg": f"{lcsql_result['msg']}, y se generó correctamente el nuevo token de acceso",
            "detail": {
                "access_token": access_token
            }
        }

    except ValueError as val_error:
        return {"status": False, "status_code": 400, "msg": str(val_error)}
    except Exception:
        logger.exception("Error inesperado al renovar el token")
        return {"status": False, "status_code": 500, "msg": INTERNAL_MSG}

async def service_logout(conn, **data)->dict:
    try:
        parametros_sp:dict={
            "p_jti": data["jti"],
            "p_user_code": data["code"]
        }
        
        save_result:dict=await repo_logout(conn,**parametros_sp)
        
        if not save_result["status"]:
            return {
                "status": False,
                "status_code": 503 if save_result.get("status_code") == 503 else 500,
                "msg": save_result["msg"]
            }
        
        return {
             "status": True,
             "msg": "Sesión cerrada exitosamente."
         }
 
        
    except ValueError as val_error:
        return {"status": False, "status_code": 400, "msg": str(val_error)}
    except Exception:
        logger.exception("Error inesperado al renovar el token")
        return {"status": False, "status_code": 500, "msg": INTERNAL_MSG}
    