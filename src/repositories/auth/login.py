from sqlalchemy import text
from repositories.general.util import execute_sp


async def repo_valid_login(conn, email: str) -> dict | None:
    # Se asignan alias en inglés a las columnas de la BD
    sql = text("""
        SELECT
            id,
            codigo AS code,
            nombre AS first_name,
            contrasena AS password
        FROM sis_usuarios
        WHERE LOWER(email_est) = LOWER(:email)
          AND anulado = FALSE
        LIMIT 1
    """)

    result = await conn.execute(sql, {"email": email})
    user = result.mappings().first()

    return dict(user) if user else None

async def repo_insert_refresh_token(conn, **data) -> dict:
    return await execute_sp(
        "sp_guardar_refresh_token",
        "Token de refresco registrado exitosamente.",
        conn,
        **data
    )

async def repo_validar_refresh_token(conn,**data)->dict:
    return await execute_sp(
        "sp_validar_refresh_token",
        "Token de refresco validado correctamente.",
        conn,
        **data
    )
    
async def repo_logout(conn,**data)->dict:
    return await execute_sp(
        "sp_anular_refresh_token",
        "Token anulado correctamente.",
        conn,
        **data
    )
