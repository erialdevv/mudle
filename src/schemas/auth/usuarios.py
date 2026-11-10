from pydantic import BaseModel, EmailStr
import uuid

class CrUsuariosRequest(BaseModel):
    nombre:str
    apellido:str
    email_est:EmailStr
    contrasena:str
    
class LeUsuariosResponse(BaseModel):
    codigo:uuid.UUID
    nombre:str
    apellido:str
    email_est:EmailStr
    anulado:bool

class AcUsuarioRequest(BaseModel):
    codigo:uuid.UUID
    nombre: str | None = None
    apellido: str | None = None
    email_est: EmailStr | None = None
    contrasena: str | None = None

class ActMultUsuariosRequest(BaseModel):
    usuarios_id: list[int]  # Lista de IDs de los usuarios a modificar
    nombre: str | None = None
    apellido: str | None = None
    email_est: EmailStr | None = None
    contrasena: str | None = None

class AnUsuariosRequest(BaseModel):
    anulado:bool

class AnMultUsuariosRequest(BaseModel):
    usuarios_id: list[int]  # Lista de IDs de los usuarios a modificar
    nombre: str | None = None
    apellido: str | None = None
    email_est: EmailStr | None = None
    contrasena: str | None = None