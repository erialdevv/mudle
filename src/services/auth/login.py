from core.security.password import verify_password
from core.security.token import create_access_token, create_refresh_token
from repositories.auth.login import repo_valid_login, repo_insert_refresh_token


async def service_login(conn, **data) -> dict:
    try:
        email: str = data["email"]
        password: str = data["password"]

        user_valid: dict | None = await repo_valid_login(conn, email)

        # 401: Credenciales inválidas
        if not user_valid:
            return {"status": False, "status_code": 401, "msg": "Correo o contraseña incorrectos."}

        # 500: Fallo interno de integridad en BD
        if not user_valid.get("password"):
            return {"status": False, "status_code": 500, "msg": "Error interno en la configuración del usuario."}

        # 401: La contraseña no coincide
        password_result: dict = verify_password(password, user_valid["password"])
        if not password_result["status"]:
            return {"status": False, "status_code": 401, "msg": "Correo o contraseña incorrectos."}

        # 500: Error interno al firmar los JWT
        access_result: dict = create_access_token(user_valid["code"], user_valid["first_name"])
        if not access_result["status"]:
            return {"status": False, "status_code": 500, "msg": access_result["msg"]}

        refresh_result: dict = create_refresh_token(user_valid["code"])
        if not refresh_result["status"]:
            return {"status": False, "status_code": 500, "msg": refresh_result["msg"]}

        access_token = access_result["detail"]["token"]
        refresh_data = refresh_result["detail"]

        sp_parameters: dict = {
            "p_id": refresh_data["token_id"],
            "p_usuario_id": user_valid["id"],
            "p_fecha_expiracion": refresh_data["exp"]
        }

        # 500: Error al guardar el refresh token en PostgreSQL
        save_result: dict = await repo_insert_refresh_token(conn, **sp_parameters)
        if not save_result["status"]:
            return {"status": False, "status_code": 500, "msg": save_result["msg"]}

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
    except Exception as error:
        return {"status": False, "status_code": 500, "msg": f"Error inesperado: {str(error)}"}
