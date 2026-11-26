from typing import Generic, TypeVar
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


# Errores que cualquier endpoint puede devolver; se documentan siempre.
COMMON_ERROR_CODES = (422, 500, 503)


# Mapa reutilizable para el parámetro `responses=` de los endpoints.
# Solo hay que indicar los códigos propios del endpoint (401, 404, 409...);
# los comunes (422, 500, 503) se agregan automáticamente.
def error_responses(*codes: int) -> dict:
    all_codes = sorted(set(codes) | set(COMMON_ERROR_CODES))
    return {
        c: {
            "model": ValidationErrorResponse if c == 422 else ErrorResponse,
            "description": _DESCRIPTIONS.get(c, "Error"),
        }
        for c in all_codes
    }


class PageMeta(BaseModel):
    """Metadatos de paginación."""
    page: int = Field(..., description="Página actual", examples=[1])
    limit: int = Field(..., description="Registros por página", examples=[10])
    total: int = Field(..., description="Total de registros que cumplen el filtro", examples=[42])
    total_pages: int = Field(..., description="Total de páginas", examples=[5])


class PaginatedResponse(BaseResponse, Generic[T]):
    """Respuesta exitosa de listados paginados."""
    detail: list[T]
    pagination: PageMeta
