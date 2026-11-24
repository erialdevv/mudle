from repositories.general.util import execute_sp, execute_query


async def repo_valid_login(conn, email: str) -> dict | None:
    # Se asignan alias en inglés a las columnas de la BD
    return await execute_query(
        """
        SELECT
            u.id,
            u.codigo AS code,
            u.nombre AS first_name,
            u.contrasena AS password,
            u.rol_id AS roleid
        FROM sis_usuarios AS u
        INNER JOIN sis_roles AS rol ON u.rol_id = rol.id
        WHERE LOWER(u.email_est) = LOWER(:email)
        AND u.anulado = FALSE
        LIMIT 1
        """,
        conn,
        email=email,
    )

async def repo_insert_refresh_token(conn, **data) -> dict:
    return await execute_sp(
        "sp_guardar_refresh_token",
        "Token de refresco registrado exitosamente.",
        conn,
        **data
    )

async def repo_get_refresh_session(conn, jti, code) -> dict | None:
    """Datos de la sesión (refresh token + usuario). Las reglas de validez las aplica el servicio.
    `expirado` se calcula en SQL para usar un único reloj (el de la BD).
    """
    return await execute_query(
        """
        SELECT
            rt.anulado AS token_anulado,
            u.anulado  AS usuario_anulado,
            (rt.fecha_expiracion <= NOW()) AS expirado,
            rt.pcid,
            u.rol_id AS roleid
        FROM refresh_tokens rt
        INNER JOIN sis_usuarios u ON u.id = rt.usuario_id
        WHERE rt.id = :jti
          AND u.codigo = :code
        """,
        conn,
        jti=jti,
        code=code,
    )

async def repo_logout(conn,**data)->dict:
    return await execute_sp(
        "sp_anular_refresh_token",
        "Token anulado correctamente.",
        conn,
        **data
    )
