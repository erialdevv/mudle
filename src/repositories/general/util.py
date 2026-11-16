import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


async def execute_sp(statement: str, success_msg: str, conn, **data) -> dict:
    """Ejecuta un procedimiento almacenado y devuelve el resultado normalizado."""
    try:
        parameters = ", ".join(f":{key}" for key in data)
        sql = text(f"CALL {statement}({parameters})")
        await conn.execute(sql, data)

        return {"status": True, "msg": success_msg}

    except SQLAlchemyError as db_error:
        original_error = getattr(db_error, "orig", db_error)

        # Registro técnico completo en el servidor para depuración
        logger.error(f"Error de BD en {statement}: {original_error}")

        clean_msg = getattr(original_error, "message", str(original_error))
        return {"status": False, "status_code": 400, "msg": clean_msg}

    except Exception as error:
        logger.error(f"Error inesperado en {statement}: {error}")
        return {
            "status": False,
            "status_code": 500,
            "msg": "Ocurrió un error interno al procesar la solicitud."
        }
