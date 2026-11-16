from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Response
from db.connection import engine
from db.config import secure_env, samesite_env, http_only_env
from schemas.auth.login import LoginRequest
from services.auth.login import service_login

router = APIRouter(
    prefix="/login",
    tags=["Login"],
)


@router.post("", status_code=status.HTTP_200_OK)
async def router_login(request: LoginRequest, response: Response):
    try:
        async with engine.begin() as conn:
            data: dict = request.model_dump()

            result: dict = await service_login(conn, **data)

            if not result["status"]:
                raise HTTPException(
                    status_code=result["status_code"],
                    detail=result["msg"]
                )

            detail: dict = result["detail"]

            now = datetime.now(timezone.utc)
            max_age_seconds = int((detail["refresh_token_exp"] - now).total_seconds())

            response.set_cookie(
                key="refresh_token",
                value=detail["refresh_token"],
                httponly=http_only_env,
                secure=secure_env,
                samesite=samesite_env,
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

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))
