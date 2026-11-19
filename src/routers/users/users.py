import logging
from fastapi import APIRouter, HTTPException, status, Request, Path, Depends
from db.connection import engine
from core.security.token import validate_acces_token
from schemas.users.users import CreateUserRequest, UpdateUserRequest, CreateUserResponse, UpdateUserResponse, GetUserResponse, BaseResponse
from schemas.general.responses import error_responses
from repositories.general.util import DB_ERROR_CODES
from services.users.users import service_update_user, service_save_user, service_get_user, service_canceled_user

logger = logging.getLogger(__name__)

# Todos los endpoints de usuarios requieren token: 401 se documenta a nivel de router.
# Los errores 422/500/503 y el manejo de excepciones inesperadas son globales.
router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses=error_responses(401),
)


def _profile_detail(data_user: dict) -> dict:
    return {
        "code": data_user["codigo"],
        "first_name": data_user["nombre"],
        "last_name": data_user["apellido"],
        "institutional_email": data_user["email_est"],
        "voided": data_user["anulado"],
    }

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateUserResponse,
    summary="Crear usuario",
    responses=error_responses(*DB_ERROR_CODES),
)
async def router_insert_user(
    body: CreateUserRequest,
    request: Request,
    token_data: dict = Depends(validate_acces_token)
):
    async with engine.begin() as conn:
        data: dict = body.model_dump()

        # El creador y el pcid vienen del token
        data["created_by"] = token_data["code"]
        data["pcid"] = token_data["pcid"]

        domains = list(request.app.state.allowed_domains)

        result: dict = await service_save_user(conn, domains, **data)

        return {"status": True, "msg": result["msg"]}

@router.get(
    "/me",
    response_model=GetUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar datos de usuario en sesión.",
    responses=error_responses(*DB_ERROR_CODES),
)
async def router_get_profile(
    token_data: dict = Depends(validate_acces_token)
):
    async with engine.begin() as conn:
        result = await service_get_user(conn, p_id=token_data["id"])

        return {
            "status": True,
            "msg": result["msg"],
            "detail": _profile_detail(result["detail"]["data_user"]),
        }

@router.get(
    "/{user_id}",
    response_model=GetUserResponse,
    summary="Trae datos de un usuario en especifico",
    status_code=status.HTTP_200_OK,
    responses=error_responses(*DB_ERROR_CODES),
)
async def router_get_user(
    user_id: int = Path(..., gt=0, description="ID del usuario a consultar"),
    token_data: dict = Depends(validate_acces_token)
):
    async with engine.begin() as conn:
        result = await service_get_user(conn, p_id=user_id)

        return {
            "status": True,
            "msg": result["msg"],
            "detail": _profile_detail(result["detail"]["data_user"]),
        }

@router.patch(
    "/update/{user_id}",
    summary="Actualizar usuario",
    status_code=status.HTTP_200_OK,
    response_model=UpdateUserResponse,
    responses=error_responses(*DB_ERROR_CODES),
)
async def router_update_user(
    request: Request,
    body: UpdateUserRequest = ...,
    user_id: int = Path(..., gt=0, description="ID del usuario a editar"),
    token_data: dict = Depends(validate_acces_token)
):
    data: dict = body.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar."
        )

    async with engine.begin() as conn:
        # El ID viaja por la URL; el editor y el pcid vienen del token
        data["id"] = user_id
        data["edited_by"] = token_data["code"]
        data["pcid"] = token_data["pcid"]

        domains = None
        if data.get("institutional_email"):
            domains = list(request.app.state.allowed_domains)

        result: dict = await service_update_user(conn, domains, **data)

        return {"status": True, "msg": result["msg"]}

@router.patch(
    "/canceled/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
    summary="Anular usuario",
    responses=error_responses(*DB_ERROR_CODES),
)
async def router_canceled_user(
    token_data: dict = Depends(validate_acces_token),
    user_id: int = Path(..., gt=0, description="ID del usuario a anular")
):
    async with engine.begin() as conn:
        result: dict = await service_canceled_user(
            conn,
            p_id=user_id,
            p_editado_por=token_data.get("code"),
        )

        return {"status": True, "msg": "Usuario anulado correctamente."}
