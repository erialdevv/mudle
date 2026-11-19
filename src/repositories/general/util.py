import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, OperationalError, InterfaceError
from core.general.errors import (
    AppError, BadRequestError, NotFoundError, ConflictError,
    UnauthorizedError, InternalError, ServiceUnavailableError,
)

logger = logging.getLogger(__name__)

_SQLSTATE_MAP: dict[str, tuple[type[AppError], str | None]] = {
    "P0001": (BadRequestError, None), 
    "P0002": (NotFoundError, None), 
    "TT401": (UnauthorizedError, None),
    "23505": (ConflictError, "Ya existe un registro con los mismos datos."),
    "23503": (ConflictError, "La operación referencia o depende de datos relacionados que no permiten completarla."),
    "23502": (BadRequestError, "Falta un dato obligatorio."),
    "23514": (BadRequestError, "Algún dato enviado no cumple las reglas de validación."),
    "22001": (BadRequestError, "Algún dato enviado excede la longitud permitida."),
    "22P02": (BadRequestError, "Algún dato enviado tiene un formato inválido."),
}

# Códigos HTTP que un SP/función puede producir según el mapa anterior (400, 404, 409).
# Los routers lo usan para documentar errores sin escribir códigos a mano:
# si se agrega un SQLSTATE al mapa, queda documentado automáticamente.
DB_ERROR_CODES: tuple[int, ...] = tuple(sorted({error.status_code for error, _ in _SQLSTATE_MAP.values()}))

_UNAVAILABLE_MSG = "El servicio de base de datos no está disponible temporalmente."


def _map_db_error(db_error: SQLAlchemyError) -> AppError:
    original_error = getattr(db_error, "orig", db_error)
    sqlstate = getattr(original_error, "sqlstate", None)

    if sqlstate in _SQLSTATE_MAP:
        error_class, generic_msg = _SQLSTATE_MAP[sqlstate]
        if generic_msg is None:
            # Mensaje controlado por el SP (sin CONTEXT ni detalles técnicos)
            diag = getattr(original_error, "diag", None)
            generic_msg = getattr(diag, "message_primary", None)
        return error_class(generic_msg)

    # Sin conexión / servidor caído / clase 08 (connection exception) / 57P (operator intervention)
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


async def execute_function(function_name: str, success_msg: str, conn, /, **data) -> dict:
    """Ejecuta una función almacenada. Sin filas lanza NotFoundError; si falla, un AppError."""
    try:
        parameters = ", ".join(f":{key}" for key in data)
        result = await conn.execute(text(f"SELECT * from {function_name}({parameters})"), data)

        row = result.mappings().first()
        if not row:
            raise NotFoundError("No se encontraron resultados.")

        return {"msg": success_msg, "data": row}

    except SQLAlchemyError as db_error:
        logger.error("Error de BD en %s: %s", function_name, getattr(db_error, "orig", db_error))
        raise _map_db_error(db_error) from db_error
