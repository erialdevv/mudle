from datetime import datetime, timedelta, timezone
import uuid
import jwt
from jwt.exceptions import PyJWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db.config import expiration_token_env, secret_key_env, algorithm_env

# Usamos HTTPBearer para pegar el token directo en /docs y enviar JSON normal en /login
security = HTTPBearer()

def create_token(code: uuid.UUID, pcid: str) -> str:
    try:
        if not secret_key_env or not algorithm_env:
            raise ValueError("Faltan variables de configuración para firmar el token.")

        time_now = datetime.now(timezone.utc)
        expiracion = time_now + timedelta(minutes=int(expiration_token_env))


        datos_token: dict = {
            "code": str(code),
            "pcid": pcid,
            "iat": time_now,
            "exp": expiracion
        }

        return jwt.encode(datos_token, secret_key_env, algorithm=algorithm_env)

    except (PyJWTError, TypeError, ValueError) as error:
        raise RuntimeError(f"Error al generar el token de acceso: {str(error)}")


def get_current_user(credenciales: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    
    credenciales_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:

        token = credenciales.credentials
        payload = jwt.decode(token, secret_key_env, algorithms=[algorithm_env])
        

        user_code: str | None = payload.get("code")
        pcid: str | None = payload.get("pcid")
        
        if user_code is None or pcid is None:
            raise credenciales_invalidas
            
        return {
            "code": uuid.UUID(user_code),
            "pcid": pcid
        }
        
    except (PyJWTError, ValueError):
        raise credenciales_invalidas
