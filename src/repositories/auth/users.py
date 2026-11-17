from repositories.general.util import execute_sp


async def repo_insert_user(conn, **data) -> dict:
    return await execute_sp(
        "sp_insertar_usuario",
        "Usuario registrado exitosamente.",
        conn,
        **data
    )


async def repo_update_user(conn, **data) -> dict:
    return await execute_sp(
        "sp_actualizar_usuario",
        "Usuario actualizado exitosamente.",
        conn,
        **data
    )


async def repo_get_user_by_id(conn,**data)->dict:
    pass