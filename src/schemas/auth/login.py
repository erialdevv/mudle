from pydantic import BaseModel, EmailStr, TypeAdapter, ValidationError, field_validator
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
            raise ValueError("No se ingreso la contrasena")
        return v

    
