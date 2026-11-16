from fastapi import APIRouter, HTTPException, status, Request
from repositories.general.startup import connect_test
from db.connection import engine

router=APIRouter(
    prefix="/config",
    tags=["Configuration"]
)

@router.get(
    "/data_in_memory", 
    status_code=status.HTTP_200_OK,
    summary="Ver datos cargados en memoria",
    description=(
        "Permite ver los datos iniciales precargados para el funcionamiento de la aplicación. "
        "**Nota:** Actualmente la respuesta se limita a la información de dominios."
    )
)

async def loaded_data(request:Request):
    valid_domains = request.app.state.allowed_domains
    if valid_domains:
        return{
            "status": True,
            "msg": "Datos cargados en memoria exitosamente",
            "database": valid_domains
        }
    return{
        "status": False,
        "msg":"La memoria está vacía",
        "database": valid_domains
    }
    
@router.get("/isconnect", status_code=status.HTTP_200_OK)
async def db_check():
    result = await connect_test(engine)
    
    is_connected, error_detail, db_name = result[0], result[1], result[2]
    
    if not is_connected:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail={
                "status": False,
                "msg": "No se pudo establecer conexión con el servidor.",
                "database": db_name,
                "technical_details": error_detail
            }
        )
        
    return {
        "status": True,
        "msg": "Conexión establecida exitosamente.",
        "database": db_name
    }
