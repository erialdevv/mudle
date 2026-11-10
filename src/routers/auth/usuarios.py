from fastapi import APIRouter, HTTPException, status
from schemas.auth.usuarios import CrUsuariosRequest,LeUsuariosResponse, AcUsuarioRequest
from services.auth.usuarios import guardar_usuario
from db.connection import engine
import uuid

router=APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
)

@router.post("registrar",status_code=status.HTTP_201_CREATED)
async def registrar_usuario(request:CrUsuariosRequest):
    try:
        async with engine.begin() as conn:
            datos=request.model_dump()
            
            datos["p_creado_por"]=uuid.UUID("157485ce-de04-4c0a-8606-fddf9ed5a3e8")
            datos["p_pcid"]="Administrador"
            
            resultado=await guardar_usuario(conn ,**datos)
   
            if not resultado["estado"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=resultado["msg"])
            
            return resultado
        
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
