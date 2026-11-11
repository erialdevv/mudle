from fastapi import APIRouter, HTTPException, status, Request
from schemas.auth.usuarios import CrUsuariosRequest,LeUsuariosResponse, AcUsuarioRequest
from services.auth.usuarios import guardar_usuario
from db.connection import engine
import uuid

router=APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
)

@router.post("/registrar",status_code=status.HTTP_201_CREATED)
async def registrar_usuario(
    request:CrUsuariosRequest,
    request_http:Request
):
    try:
        async with engine.begin() as conn:
            datos=request.model_dump()
            
            datos["p_creado_por"]=uuid.UUID("157485ce-de04-4c0a-8606-fddf9ed5a3e8")
            datos["p_editado_por"]=datos["p_creado_por"]
            datos["p_pcid"]="Administrador"
            
            dominios=request_http.app.state.dominios_permitidos
            
            resultado=await guardar_usuario(conn ,dominios,**datos)
   
            if not resultado["estado"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=resultado["msg"])
            
            return resultado
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
