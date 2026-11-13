from datetime import datetime, timedelta, timezone
import uuid
import jwt
from jwt.exceptions import PyJWTError
from fastapi.security import HTTPBearer
from db.config import expiration_token_env, secret_key_env, algorithm_env

security = HTTPBearer()

def create_token(code: uuid.UUID, pcid: str) -> str:
    try:
        if not secret_key_env or not algorithm_env:
            raise ValueError("Faltan variables de configuración para firmar el token.")

        time_now = datetime.now(timezone.utc)
        expiracion = time_now + timedelta(minutes=int(expiration_token_env))

        datos_token: dict = {
            "user_code": str(code),
            "pcid": pcid,
            "iat": time_now,
            "exp": expiracion
        }

        return jwt.encode(datos_token, secret_key_env, algorithm=algorithm_env)

    except (PyJWTError, TypeError, ValueError) as error:
        raise RuntimeError(f"Error al generar el token de acceso: {str(error)}")
