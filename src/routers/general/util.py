import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from core.security.token import validate_acces_token
from repositories.general.startup import connect_test
from db.connection import engine
from schemas.general.config import DataInMemoryResponse, DbConnectionResponse, DbConnectionErrorResponse
from schemas.general.responses import error_responses

logger = logging.getLogger(__name__)

router=APIRouter(
    prefix="/config",
    tags=["Configuration"],
    dependencies=[Depends(validate_acces_token)],
)

@router.get(
    "/data_in_memory", 
    status_code=status.HTTP_200_OK,
    response_model=DataInMemoryResponse,
    summary="Ver datos cargados en memoria",
    description=(
        "Permite ver los datos iniciales precargados para el funcionamiento de la aplicación. "
        "**Nota:** Actualmente la respuesta se limita a la información de dominios."
    ),
    responses=error_responses(401, 503),
)

async def loaded_data(request:Request):
    valid_domains = request.app.state.allowed_domains
    if valid_domains:
        return{
            "status": True,
            "msg": "Datos cargados en memoria exitosamente",
            "database": valid_domains
        }
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Los datos de configuración aún no están cargados en memoria."
    )
    
@router.get(
    "/isconnect",
    status_code=status.HTTP_200_OK,
    response_model=DbConnectionResponse,
    summary="Probar conexión a la base de datos",
    responses={
        **error_responses(401),
        503: {"model": DbConnectionErrorResponse, "description": "No se pudo conectar a la base de datos"},
    },
)
async def db_check():
    result = await connect_test(engine)
    
    is_connected, error_detail, db_name = result[0], result[1], result[2]
    
    if not is_connected:
        # El detalle técnico solo se registra en el servidor
        logger.error("Fallo en la prueba de conexión a la BD: %s", error_detail)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": False,
                "msg": "No se pudo establecer conexión con el servidor.",
                "database": db_name
            }
        )
        
    return {
        "status": True,
        "msg": "Conexión establecida exitosamente.",
        "database": db_name
    }
