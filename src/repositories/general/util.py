import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, OperationalError, InterfaceError
from core.general.errors import (
    AppError, BadRequestError, ConflictError,
    InternalError, ServiceUnavailableError,
)

logger = logging.getLogger(__name__)

# Las reglas de negocio viven en Python (servicios). Este mapa solo traduce los errores
# que la propia BD puede producir como red de seguridad (constraints) o por infraestructura.
_SQLSTATE_MAP: dict[str, tuple[type[AppError], str | None]] = {
    "23505": (ConflictError, "Ya existe un registro con los mismos datos."),
    "23503": (ConflictError, "La operación referencia o depende de datos relacionados que no permiten completarla."),
    "23502": (BadRequestError, "Falta un dato obligatorio."),
    "23514": (BadRequestError, "Algún dato enviado no cumple las reglas de validación."),
    "22001": (BadRequestError, "Algún dato enviado excede la longitud permitida."),
    "22P02": (BadRequestError, "Algún dato enviado tiene un formato inválido."),
}


# Códigos que un constraint de la BD puede producir (400, 409); se usa para documentar en Swagger
DB_ERROR_CODES: tuple[int, ...] = tuple(sorted({error.status_code for error, _ in _SQLSTATE_MAP.values()}))
_UNAVAILABLE_MSG = "El servicio de base de datos no está disponible temporalmente."


def _map_db_error(db_error: SQLAlchemyError) -> AppError:
    
    original_error = getattr(db_error, "orig", db_error)
    sqlstate = getattr(original_error, "sqlstate", None)

    if sqlstate in _SQLSTATE_MAP:
        error_class, generic_msg = _SQLSTATE_MAP[sqlstate]
        return error_class(generic_msg)

    #errores no controlados
    is_connection_error = sqlstate is None and isinstance(db_error, (OperationalError, InterfaceError))
    if is_connection_error or (sqlstate or "").startswith(("08", "57P", "53")):
        return ServiceUnavailableError(_UNAVAILABLE_MSG)

    return InternalError()


async def execute_sp(statement: str, success_msg: str, conn, /, **data) -> dict:
    """Ejecuta un procedimiento almacenado. Si falla, lanza un AppError."""
    try:
        parameters = ", ".join(f":{key}" for key in data)
        await conn.execute(text(f"CALL {statement}({parameters})"), data)
        return {"msg": success_msg}

    except SQLAlchemyError as db_error:
        # Detalle técnico solo en el log del servidor, nunca en la respuesta
        logger.error("Error de BD en %s: %s", statement, getattr(db_error, "orig", db_error))
        raise _map_db_error(db_error) from db_error


async def execute_query(sql: str, conn, /, **params) -> dict | None:
    """Ejecuta un SELECT y devuelve la primera fila como dict, o None si no hay filas.

    Decidir si "sin filas" es un error (404, 401...) es responsabilidad del servicio.
    """
    try:
        result = await conn.execute(text(sql), params)
        row = result.mappings().first()
        return dict(row) if row else None

    except SQLAlchemyError as db_error:
        logger.error("Error de BD en consulta: %s", getattr(db_error, "orig", db_error))
        raise _map_db_error(db_error) from db_error


async def execute_function(function_name: str, success_msg: str, conn, /, **data) -> dict:
    """Ejecuta una función almacenada. `data` es None si no devolvió filas; el servicio decide qué hacer."""
    parameters = ", ".join(f":{key}" for key in data)
    row = await execute_query(f"SELECT * FROM {function_name}({parameters})", conn, **data)

    return {"msg": success_msg, "data": row}
