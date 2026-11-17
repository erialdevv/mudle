import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, OperationalError, InterfaceError

logger = logging.getLogger(__name__)

# SQLSTATE de PostgreSQL -> (status HTTP, mensaje genérico). None = usar el mensaje del SP.
# Para que un SP devuelva 404/409 con mensaje propio:
#   RAISE EXCEPTION 'Usuario no encontrado' USING ERRCODE = 'P0002';  -- 404
#   RAISE EXCEPTION 'El correo ya existe'   USING ERRCODE = '23505';  -- 409
_SQLSTATE_MAP: dict[str, tuple[int, str | None]] = {
    "P0001": (400, None),  # raise_exception (RAISE EXCEPTION sin ERRCODE): mensaje del SP
    "P0002": (404, None),  # no_data_found: mensaje del SP
    "23505": (409, "Ya existe un registro con los mismos datos."),
    "23503": (409, "La operación referencia o depende de datos relacionados que no permiten completarla."),
    "23502": (400, "Falta un dato obligatorio."),
    "23514": (400, "Algún dato enviado no cumple las reglas de validación."),
    "22001": (400, "Algún dato enviado excede la longitud permitida."),
    "22P02": (400, "Algún dato enviado tiene un formato inválido."),
}

_INTERNAL_MSG = "Ocurrió un error interno al procesar la solicitud."
_UNAVAILABLE_MSG = "El servicio de base de datos no está disponible temporalmente."


def _map_db_error(db_error: SQLAlchemyError) -> dict:
    original_error = getattr(db_error, "orig", db_error)
    sqlstate = getattr(original_error, "sqlstate", None)

    if sqlstate in _SQLSTATE_MAP:
        status_code, generic_msg = _SQLSTATE_MAP[sqlstate]
        if generic_msg is None:
            # Mensaje controlado por el SP (sin CONTEXT ni detalles técnicos)
            diag = getattr(original_error, "diag", None)
            generic_msg = getattr(diag, "message_primary", None) or _INTERNAL_MSG
        return {"status": False, "status_code": status_code, "msg": generic_msg}

    # Sin conexión / servidor caído / clase 08 (connection exception) / 57P (operator intervention)
    is_connection_error = sqlstate is None and isinstance(db_error, (OperationalError, InterfaceError))
    if is_connection_error or (sqlstate or "").startswith(("08", "57P", "53")):
        return {"status": False, "status_code": 503, "msg": _UNAVAILABLE_MSG}

    return {"status": False, "status_code": 500, "msg": _INTERNAL_MSG}


async def execute_sp(statement: str, success_msg: str, conn, **data) -> dict:
    """Ejecuta un procedimiento almacenado y devuelve el resultado normalizado."""
    try:
        parameters = ", ".join(f":{key}" for key in data)
        sql = text(f"CALL {statement}({parameters})")
        await conn.execute(sql, data)

        return {"status": True, "msg": success_msg}

    except SQLAlchemyError as db_error:
        # Detalle técnico solo en el log del servidor, nunca en la respuesta
        logger.error("Error de BD en %s: %s", statement, getattr(db_error, "orig", db_error))
        return _map_db_error(db_error)

    except Exception:
        logger.exception("Error inesperado en %s", statement)
        return {"status": False, "status_code": 500, "msg": _INTERNAL_MSG}
    
async def excecute_function(function:str,succes_msg:str, conn,**data)->dict:
     """Ejecuta un funcion almacenado y devuelve el resultado normalizado."""
     try:
        parameters = ", ".join(f":{key}" for key in data)
        sql=text(f"SELECT {function}")
         
     except SQLAlchemyError as db_error:
        # Detalle técnico solo en el log del servidor, nunca en la respuesta
        logger.error("Error de BD en %s: %s", function, getattr(db_error, "orig", db_error))
        return _map_db_error(db_error)
        
