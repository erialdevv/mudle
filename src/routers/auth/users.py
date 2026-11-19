import logging
from fastapi import APIRouter, HTTPException, status, Request, Path, Depends
from db.connection import engine
from core.security.token import validate_acces_token
from schemas.auth.users import CreateUserRequest, UpdateUserRequest, CreateUserResponse, UpdateUserResponse, GetUserResponse
from schemas.general.responses import error_responses, http_error_from_result
from services.auth.users import service_update_user, service_save_user, service_get_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateUserResponse,
    summary="Crear usuario",
    responses=error_responses(400, 401, 409, 422, 500, 503),
)
async def router_insert_user(
    body: CreateUserRequest,
    request: Request,
    token_data: dict = Depends(validate_acces_token)
):
    try:
        async with engine.begin() as conn:
            data: dict = body.model_dump()

            # El creador y el pcid vienen del token
            data["created_by"] = token_data["code"]
            data["pcid"] = token_data["pcid"]

            domains = list(request.app.state.allowed_domains)

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

@router.get(
    "/me",
    response_model=GetUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar datos de usuario en sesión.",
)
async def router_get_profile(
    token_data: dict = Depends(validate_acces_token)
):
    try:
        async with engine.begin() as conn:
            sp_parameters:dict={
                "p_id":token_data["id"]
            }
            
            result=await service_get_user(conn, **sp_parameters)
            
            
            if not result["status"]:
                raise http_error_from_result(result)
            
            detail:dict=result["detail"]["data_user"]
            
            return{
                "status":True,
                "msg":result["msg"],
                "detail":{
                    "code":detail["codigo"],
                    "first_name":detail["nombre"],
                    "last_name":detail["apellido"],
                    "institutional_email":detail["email_est"],
                    "voided":detail["anulado"]
                }
            }
            
    except HTTPException:
            raise
    except Exception:
            logger.exception("Error inesperado en %s", "GET /users/me")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ocurrió un error interno al procesar la solicitud."
            )

@router.get(
    "/{user_id}",
    response_model=GetUserResponse,
    summary="Trae datos de un usuario en especifico",
    status_code=status.HTTP_200_OK
)
async def router_get_user(
    user_id: int = Path(..., gt=0, description="ID del usuario a consultar"),
    token_data: dict = Depends(validate_acces_token)
):
    try:

        async with engine.begin() as conn:
            sp_parameters:dict={
                "p_id":user_id
            }
            result=await service_get_user(conn,**sp_parameters)
            detail:dict=result["detail"]["data_user"]

            if not result["status"]:
                raise http_error_from_result(result)

            return{
                "status":True,
                "msg":result["msg"],
                "detail":{
                    "code":detail["codigo"],
                    "first_name":detail["nombre"],
                    "last_name":detail["apellido"],
                    "institutional_email":detail["email_est"],
                    "voided":detail["anulado"]
                }
            }
            
    except HTTPException:
            raise
    except Exception:
            logger.exception("Error inesperado en %s", "GET /users/{user_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ocurrió un error interno al procesar la solicitud."
            )

@router.patch(
    "/update/{user_id}",
    summary="Actualizar usuario",
    status_code=status.HTTP_200_OK,
    response_model=UpdateUserResponse,
    responses=error_responses(400, 401, 404, 409, 422, 500, 503),
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

    try:
        async with engine.begin() as conn:

            # El ID viaja por la URL; el editor y el pcid vienen del token
            data["id"] = user_id
            data["edited_by"] = token_data["code"]
            data["pcid"] = token_data["pcid"]

            domains = None
            if data.get("institutional_email"):
                domains = list(request.app.state.allowed_domains)

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

