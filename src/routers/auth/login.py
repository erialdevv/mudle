import logging
from datetime import datetime, timezone
from fastapi import APIRouter, status, Response, Depends
from db.connection import engine
from db.config import CookieConfig
from schemas.auth.login import LoginRequest, LoginResponse, RefreshResponse
from schemas.general.responses import error_responses, BaseResponse
from services.auth.login import service_login, service_validate_token, service_logout
from core.security.token import validate_refresh_token

logger = logging.getLogger(__name__)

# Los errores 422/500/503 y el manejo de excepciones inesperadas son globales.
router = APIRouter(
    prefix="/auth",
    tags=["Login"],
)

@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
    summary="Iniciar sesión",
    description="Valida credenciales y devuelve el access token. El refresh token se entrega en cookie HttpOnly.",
    responses=error_responses(401),
)
async def router_login(body: LoginRequest, response: Response):
    async with engine.begin() as conn:
        result: dict = await service_login(conn, **body.model_dump())


        detail: dict = result["detail"]

        now = datetime.now(timezone.utc)
        max_age_seconds = int((detail["refresh_token_exp"] - now).total_seconds())

        response.set_cookie(
            key="refresh_token",
            value=detail["refresh_token"],
            httponly=CookieConfig.http_only,
            secure=CookieConfig.secure,
            samesite=CookieConfig.samesite,
            path="/auth",
            max_age=max_age_seconds
        )

        return {
            "status": True,
            "msg": result["msg"],
            "detail": {
                "user_id": detail["user_id"],
                "access_token": detail["access_token"],
                "token_type": "bearer"
            }
        }


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=RefreshResponse,
    summary="Renovar access token",
    description="Genera un nuevo access token a partir del refresh token almacenado en la cookie.",
    responses=error_responses(401),
)
async def router_refresh(data_refresh_token=Depends(validate_refresh_token)):
    async with engine.begin() as conn:
        result = await service_validate_token(conn, **data_refresh_token)


        detail: dict = result["detail"]

        return {
            "status": True,
            "msg": result["msg"],
            "detail": {
                "access_token": detail["access_token"],
                "token_type": "bearer"
            }
        }


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
    summary="Salida segura de la sesión",
    description="Endpoint para cerrar una sesión, anulando tokens de sesión y eliminando el token de la cookie",
    responses=error_responses(401),
)
async def router_logout(response: Response, data_refresh_token=Depends(validate_refresh_token)):
    async with engine.begin() as conn:
        result = await service_logout(conn, **data_refresh_token)


        response.delete_cookie(
            key="refresh_token",
            httponly=CookieConfig.http_only,
            secure=CookieConfig.secure,
            samesite=CookieConfig.samesite,
            path="/auth",
        )

        return {"status": True, "msg": result["msg"]}
