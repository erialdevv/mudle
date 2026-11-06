from fastapi import APIRouter
from fastapi import FastAPI, HTTPException,status,Request
from repositories.general.arranque import connect_test
from db.connection import engine

router=APIRouter(
    prefix="/config",
    tags=["Configuracion"]
)

@router.get(
    "/data_in_memory", 
    status_code=status.HTTP_200_OK,
    summary="Visualizar datos cargados en memoria",
    description=(
        "Permite visualizar los datos iniciales precargados para el funcionamiento de la aplicación. "
        "**Nota:** Actualmente, la respuesta está limitada únicamente a la información de los dominios."
    )
)

async def datos_cargados(request:Request):
    dominios_validos = request.app.state.dominios_permitidos
    if dominios_validos:
        return{
            "status": True,
            "message": "Datos cargados en memoria correctamente",
            "database": dominios_validos
        }
    return{
        "status":False,
        "message":"Memoria vacia",
        "database": dominios_validos
    }
    
@router.get("/isconnect", status_code=status.HTTP_200_OK)
async def db_check():
    resultado = await connect_test(engine)
    
    is_connected, error_detail, db_name = resultado[0], resultado[1], resultado[2]
    
    if not is_connected:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail={
                "status": "error",
                "message": "No se pudo establecer la conexión con el servidor.",
                "database": db_name,
                "technical_details": error_detail
            }
        )
        
    return {
        "status": "success",
        "message": "Conexión establecida exitosamente.",
        "database": db_name
    }
