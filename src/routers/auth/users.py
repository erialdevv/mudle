import logging
from fastapi import APIRouter, HTTPException, status, Request, Path, Depends
from db.connection import engine
from core.security.token import validate_acces_token
from schemas.auth.users import CreateUserRequest, UpdateUserRequest, CreateUserResponse, UpdateUserResponse
from schemas.general.responses import error_responses, http_error_from_result
from services.auth.users import service_update_user, service_save_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateUserResponse,
    summary="Crear usuario",
    responses=error_responses(400, 401, 409, 422, 500, 503),
)
async def router_insert_user(
    request: CreateUserRequest,
    request_http: Request,
    token_data: dict = Depends(validate_acces_token)
):
    try:
        async with engine.begin() as conn:
            data: dict = request.model_dump()

            # El creador y el pcid vienen del token
            data["created_by"] = token_data["code"]
            data["pcid"] = token_data["pcid"]

            domains = list(request_http.app.state.allowed_domains)

            result: dict = await service_save_user(conn, domains, **data)

            if not result["status"]:
                raise http_error_from_result(result)

            return {"status": True, "msg": result["msg"]}

    except HTTPException:
        raise
    except Exception:
        logger.exception("Error inesperado en %s", "POST /users")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error interno al procesar la solicitud."
        )


@router.patch(
    "/update/{id}",
    summary="Actualizar usuario",
    status_code=status.HTTP_200_OK,
    response_model=UpdateUserResponse,
    responses=error_responses(400, 401, 404, 409, 422, 500, 503),
)
async def router_update_user(
    request_http: Request,
    body: UpdateUserRequest = ...,
    id: int = Path(..., gt=0, description="ID del usuario a editar"),
    token_data: dict = Depends(validate_acces_token)
):
    data: dict = body.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar."
        )

    try:
        async with engine.begin() as conn:

            # El ID viaja por la URL; el editor y el pcid vienen del token
            data["id"] = id
            data["edited_by"] = token_data["code"]
            data["pcid"] = token_data["pcid"]

            domains = None
            if data.get("institutional_email"):
                domains = list(request_http.app.state.allowed_domains)

            result: dict = await service_update_user(conn, domains, **data)

            if not result["status"]:
                raise http_error_from_result(result)

            return {"status": True, "msg": result["msg"]}

    except HTTPException:
        raise
    except Exception:
        logger.exception("Error inesperado en %s", "PATCH /users/update/{id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error interno al procesar la solicitud."
        )
