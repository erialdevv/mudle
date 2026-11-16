import uuid
from fastapi import APIRouter, HTTPException, status, Request, Path, Depends
from db.connection import engine
from core.security.token import get_current_user
from schemas.auth.users import CreateUserRequest, UpdateUserRequest
from services.auth.users import service_update_user, service_save_user

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post("", status_code=status.HTTP_201_CREATED)
async def router_insert_user(
    request: CreateUserRequest,
    request_http: Request
):
    try:
        async with engine.begin() as conn:
            data: dict = request.model_dump()

            # Valores fijos temporales para desarrollo; en producción vendrán del token
            data["created_by"] = uuid.UUID("157485ce-de04-4c0a-8606-fddf9ed5a3e8")
            data["pcid"] = "Administrador"

            domains = list(request_http.app.state.allowed_domains)

            result: dict = await service_save_user(conn, domains, **data)

            if not result["status"]:
                raise HTTPException(status_code=result["status_code"], detail=result["msg"])

            return {"status": True, "msg": result["msg"]}

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))


@router.get("/me", status_code=status.HTTP_200_OK)
async def router_get_user():
    pass


@router.patch("/update/{id}", summary="Actualizar usuario", status_code=status.HTTP_200_OK)
async def router_update_user(
    request_http: Request,
    body: UpdateUserRequest = ...,
    id: str = Path(..., description="ID del usuario a editar"),
    token_data: dict = Depends(get_current_user)
):
    try:
        async with engine.begin() as conn:
            data: dict = body.model_dump(exclude_unset=True)

            # El ID viaja por la URL; el editor y el pcid vienen del token
            data["id"] = id
            data["edited_by"] = token_data["code"]
            data["pcid"] = token_data["pcid"]

            domains = None
            if data.get("institutional_email"):
                domains = list(request_http.app.state.allowed_domains)

            result: dict = await service_update_user(conn, domains, **data)

            if not result["status"]:
                raise HTTPException(status_code=result["status_code"], detail=result["msg"])

            return {"status": True, "msg": result["msg"]}

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))
