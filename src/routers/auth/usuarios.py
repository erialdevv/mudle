from fastapi import APIRouter, HTTPException, status
from schemas.auth.usuarios import CrUsuariosRequest,LeUsuariosResponse, AcUsuarioRequest

router=APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
)