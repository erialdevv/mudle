from pydantic import BaseModel, EmailStr, Field, TypeAdapter, ValidationError, field_validator
from schemas.general.responses import DataResponse
email_adapter = TypeAdapter(EmailStr)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
    @field_validator("email")
    @staticmethod
    def validate_email(v: str) -> str:
        if not v or not v.strip():
            raise ValueError("No se ingresó el correo electrónico")
        try:
            return email_adapter.validate_python(v.strip())
        except ValidationError:
            raise ValueError("El formato del correo electrónico no es válido")

    @field_validator("password")
    @staticmethod
    def validate_password(v: str) -> str:
        if not v or not v.strip():
            raise ValueError("No se ingresó la contraseña")
        return v


class LoginDetail(BaseModel):
    user_id: int = Field(..., description="Identificador del usuario", examples=[1])
    access_token: str = Field(..., description="JWT de acceso")
    token_type: str = Field(default="bearer", examples=["bearer"])


class LoginResponse(DataResponse[LoginDetail]):
    """Respuesta del login. El refresh token viaja en la cookie HttpOnly `refresh_token`."""


class RefreshDetail(BaseModel):
    access_token: str = Field(..., description="Nuevo JWT de acceso")
    token_type: str = Field(default="bearer", examples=["bearer"])


class RefreshResponse(DataResponse[RefreshDetail]):
    """Respuesta de renovación del access token."""
