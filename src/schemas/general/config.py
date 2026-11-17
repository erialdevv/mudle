from pydantic import BaseModel, Field
from schemas.general.responses import BaseResponse


class DataInMemoryResponse(BaseResponse):
    """Datos precargados en memoria (actualmente solo dominios permitidos)."""
    database: list[str] | set[str] | None = Field(
        default=None, description="Dominios permitidos cargados en memoria", examples=[["empresa.com"]]
    )


class DbConnectionResponse(BaseResponse):
    """Resultado de la prueba de conexión a la base de datos."""
    database: str | None = Field(default=None, description="Nombre de la base de datos", examples=["mudle"])


class DbConnectionErrorResponse(BaseModel):
    """Error 503 de /config/isconnect (el `detail` es un objeto)."""
    detail: DbConnectionResponse
