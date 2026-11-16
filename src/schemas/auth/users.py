import uuid
from typing import Annotated
from pydantic import BaseModel, EmailStr, StringConstraints, field_validator,model_validator, Field


NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]

class CreateUserRequest(BaseModel):
    first_name: NonEmptyStr = Field(..., description="Nombre del empleado", examples=["Juan"])
    last_name: NonEmptyStr = Field(..., description="Apellido del empleado", examples=["Pérez"])
    institutional_email: EmailStr = Field(..., description="Correo institucional", examples=["jperez@empresa.com"])
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        pattern=r".*\S.*",  # Exige que haya al menos un carácter que no sea espacio en blanco
        description="Contraseña de al menos 8 caracteres (no puede ser solo espacios)",
        examples=["ClaveSegura2026*"]
    )
    
class ReadUserRequest(BaseModel):
    id:int=Field(...,gt=0, description="El ID del usuario debe ser un número entero mayor a 0")

class ReadUserResponse(BaseModel):
    code:uuid.UUID
    first_name:str
    last_name:str
    institutional_email:EmailStr
    voided:bool

class UpdateUserRequest(BaseModel):
    
    first_name: NonEmptyStr | None = Field(
        default=None, 
        description="Nuevo nombre del usuario"
    )
    last_name: NonEmptyStr | None = Field(
        default=None, 
        description="Nuevo apellido del usuario"
    )
    institutional_email: EmailStr | None = Field(
        default=None, 
        description="Nuevo correo institucional"
    )
    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=128,
        pattern=r".*\S.*",
        description="Nueva contraseña (mínimo 8 caracteres, no puede ser solo espacios)"
    )

class UpdateMultipleUsersRequest(BaseModel):
    user_ids: list[int]  # Lista de IDs de los usuarios a modificar
    first_name: str | None = None
    last_name: str | None = None
    institutional_email: EmailStr | None = None
    password: str | None = None

class VoidUserRequest(BaseModel):
    voided:bool

class VoidMultipleUsersRequest(BaseModel):
    user_ids: list[int]  # Lista de IDs de los usuarios a modificar
    first_name: str | None = None
    last_name: str | None = None
    institutional_email: EmailStr | None = None
    password: str | None = None
