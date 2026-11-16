from datetime import datetime, timedelta, timezone
import uuid
import jwt
from jwt.exceptions import PyJWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db.config import exp_access_token_env, exp_refresh_token_env, secret_key_env, algorithm_env

# Se usa HTTPBearer para pegar el token directo en /docs y enviar JSON normal en /login
security = HTTPBearer()


def create_access_token(code: uuid.UUID, pcid: str) -> dict:
    try:
        if not secret_key_env or not algorithm_env:
            raise ValueError("Faltan variables de configuración para firmar el token.")

        time_now = datetime.now(timezone.utc)
        expiration = time_now + timedelta(minutes=int(exp_access_token_env))

        token_payload: dict = {
            "sub": str(code),
            "pcid": pcid,
            "iat": time_now,
            "exp": expiration
        }

        return {
            "status": True,
            "msg": "Token de acceso creado exitosamente.",
            "detail": {
                "token": jwt.encode(token_payload, secret_key_env, algorithm=algorithm_env)
            }
        }

    except (PyJWTError, TypeError, ValueError) as error:
        return {
            "status": False,
            "msg": f"Error al generar el token de acceso: {str(error)}",
            "detail": {}
        }


def create_refresh_token(code: uuid.UUID) -> dict:
    try:
        if not secret_key_env or not algorithm_env:
            raise ValueError("Faltan variables de configuración para firmar el token.")

        time_now = datetime.now(timezone.utc)
        expiration = time_now + timedelta(minutes=int(exp_refresh_token_env))
        token_id = uuid.uuid4()

        token_payload: dict = {
            "sub": str(code),
            "exp": expiration,
            "jti": str(token_id)
        }

        return {
            "status": True,
            "msg": "Token de refresco creado exitosamente.",
            "detail": {
                "token": jwt.encode(token_payload, secret_key_env, algorithm=algorithm_env),
                "token_id": token_id,
                "exp": expiration
            }
        }

    except (PyJWTError, TypeError, ValueError) as error:
        return {
            "status": False,
            "msg": f"Error al generar el token de refresco: {str(error)}",
            "detail": {}
        }


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:

    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, secret_key_env, algorithms=[algorithm_env])

        user_code: str | None = payload.get("sub")
        pcid: str | None = payload.get("pcid")

        if user_code is None or pcid is None:
            raise invalid_credentials

        return {
            "code": uuid.UUID(user_code),
            "pcid": pcid
        }

    except (PyJWTError, ValueError):
        raise invalid_credentials
