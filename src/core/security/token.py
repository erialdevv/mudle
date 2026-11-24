from datetime import datetime, timedelta, timezone
import uuid
import jwt
from jwt.exceptions import PyJWTError
from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db.config import TokenConfig

# Se usa HTTPBearer para pegar el token directo en /docs y enviar JSON normal en /login
security = HTTPBearer()


def create_access_token(
    user_id: int, 
    code: uuid.UUID,
    roleid:int,
    role_version:int,
    perms:dict,
    pcid: str
    ) -> dict:
    try:
        if not TokenConfig.secret_key or not TokenConfig.algorithm:
            raise ValueError("Faltan variables de configuración para firmar el token.")

        time_now = datetime.now(timezone.utc)
        expiration = time_now + timedelta(minutes=int(TokenConfig.exp_access_token))

        token_payload: dict = {
            "sub": str(code),
            "rol_id":roleid,
            "version":role_version,
            "perms":perms,
            "uid": user_id,
            "pcid": pcid,
            "iat": time_now,
            "exp": expiration,
            "type":"access"
        }

        return {
            "status": True,
            "msg": "Token de acceso creado exitosamente.",
            "detail": {
                "token": jwt.encode(token_payload, TokenConfig.secret_key, algorithm=TokenConfig.algorithm)
            }
        }

    except (PyJWTError, TypeError, ValueError) as error:
        return {
            "status": False,
            "msg": f"Error al generar el token de acceso: {str(error)}",
            "detail": {}
        }


def create_refresh_token(user_id: int, code: uuid.UUID, pcid: str) -> dict:
    try:
        if not TokenConfig.secret_key or not TokenConfig.algorithm:
            raise ValueError("Faltan variables de configuración para firmar el token.")

        time_now = datetime.now(timezone.utc)
        expiration = time_now + timedelta(minutes=int(TokenConfig.exp_refresh_token))
        token_id = uuid.uuid4()

        token_payload: dict ={
            "sub": str(code),
            "uid": user_id,
            "pcid": pcid,
            "exp": expiration,
            "jti": str(token_id),
            "type":"refresh"
        }

        return {
            "status": True,
            "msg": "Token de refresco creado exitosamente.",
            "detail": {
                "token": jwt.encode(token_payload, TokenConfig.secret_key_refresh, algorithm=TokenConfig.algorithm),
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


def validate_acces_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:

    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token, 
            TokenConfig.secret_key, 
            algorithms=[TokenConfig.algorithm],
            options={
                "require": ["exp","sub","uid","type"]
            }
        )

        user_code: str | None = payload.get("sub")
        user_id: int | None = payload.get("uid")
        pcid: str | None = payload.get("pcid")
        type_token=payload.get("type")
        role_id=payload.get("rol_id")
        version=payload.get("version")
        
        if type_token!=TokenConfig.token_type_access:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="El token enviado no es un token de acceso",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if user_code is None or pcid is None or not isinstance(user_id, int) or isinstance(user_id, bool):
            raise invalid_credentials

        return {
            "id": user_id,
            "code": uuid.UUID(user_code),
            "rol_id":role_id,
            "pcid": pcid,
            "version":version
        }

    except (PyJWTError, ValueError):
        raise invalid_credentials


def validate_refresh_token(refresh_token: str | None = Cookie(default=None)) -> dict:
    
    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado"
    )
    
    if not refresh_token:
        raise invalid_credentials

    try:
        payload = jwt.decode(
            refresh_token, 
            TokenConfig.secret_key_refresh, 
            algorithms=[TokenConfig.algorithm],
            options={"require": ["exp", "sub", "uid", "jti", "type"]}
        )
        
        user_code: str = payload["sub"]
        jti: str = payload["jti"]
        type_token: str = payload["type"]
        user_id: int | None = payload["uid"]
        pcid: str | None = payload.get("pcid")
        
        if pcid is None or not isinstance(user_id, int) or isinstance(user_id, bool) or type_token != TokenConfig.token_type_refresh:
            raise invalid_credentials
        
        return {
            "jti": uuid.UUID(jti),
            "id": user_id,
            "code": uuid.UUID(user_code),
            "pcid": pcid     
        }
        
    except (PyJWTError, ValueError):
        raise invalid_credentials
