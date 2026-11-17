from typing import Generic, TypeVar
from fastapi import HTTPException
from pydantic import BaseModel, Field

T = TypeVar("T")

class BaseResponse(BaseModel):
    """Estructura base de toda respuesta exitosa."""
    status: bool = Field(..., description="Indica si la operación fue exitosa", examples=[True])
    msg: str = Field(..., description="Mensaje descriptivo del resultado")


class DataResponse(BaseResponse, Generic[T]):
    """Respuesta exitosa que incluye un bloque `detail` con datos."""
    detail: T


class ErrorResponse(BaseModel):
    """Formato de error generado por HTTPException (FastAPI)."""
    detail: str = Field(..., description="Descripción del error", examples=["Credenciales inválidas"])


class ValidationErrorItem(BaseModel):
    loc: list[str | int] = Field(..., description="Ubicación del campo con error", examples=[["body", "email"]])
    msg: str = Field(..., description="Descripción del error de validación", examples=["value is not a valid email address"])
    type: str = Field(..., description="Tipo de error de validación", examples=["value_error"])


class ValidationErrorResponse(BaseModel):
    """Formato de error 422 generado por FastAPI/Pydantic (lista de errores por campo)."""
    detail: list[ValidationErrorItem]


def http_error_from_result(result: dict) -> HTTPException:
    """Convierte el resultado fallido de un servicio en HTTPException.

    Si el servicio indica un campo (`field`) con 422, usa el mismo formato de lista
    que genera FastAPI para errores de validación, para que coincida con Swagger.
    """
    status_code = result["status_code"]
    if status_code == 422 and result.get("field"):
        detail = [{"loc": ["body", result["field"]], "msg": result["msg"], "type": "value_error"}]
        return HTTPException(status_code=422, detail=detail)
    return HTTPException(status_code=status_code, detail=result["msg"])


_DESCRIPTIONS = {
    400: "Solicitud incorrecta: datos que no cumplen las reglas de negocio",
    401: "No autenticado o token inválido/expirado",
    403: "Sin permisos",
    404: "Recurso no encontrado",
    409: "Conflicto con datos existentes",
    422: "Error de validación de formato en los datos enviados",
    500: "Error interno del servidor",
    503: "Servicio no disponible temporalmente",
}


# Mapa reutilizable para el parámetro `responses=` de los endpoints
def error_responses(*codes: int) -> dict:
    return {
        c: {
            "model": ValidationErrorResponse if c == 422 else ErrorResponse,
            "description": _DESCRIPTIONS.get(c, "Error"),
        }
        for c in codes
    }
