from repositories.general.util import execute_sp, execute_function


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
    return await execute_function(
        "fn_obtener_usuario_por_id",
        "Consulta de perfil realizada correctamente",
        conn,
        **data
    )

async def repo_canceled_user_by_id(conn,**data)->dict:
    return await execute_sp(
        "sp_anular_usuario",
        "Anulacion de usuario completada correctamente.",
        conn,
        **data
    )