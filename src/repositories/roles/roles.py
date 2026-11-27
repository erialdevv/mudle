from repositories.general.util import execute_sp, execute_function

async def repo_insert_roles(conn,**data):
    return await execute_sp(
        "sp_insertar_rol",
        "Rol creado exitosamente",
        conn,
        **data
    )

async def repo_get_roles_me(conn,**data):
    return await execute_function(
        "fn_obtener_rol_por_id",
        "Rol encontrado correctamente",
        conn,
        **data
    )

async def repo_get_all_roles(conn,**data):
    return await execute_function(
        "fn_obtener_roles",
        "Roles cargados correctamente",
        conn,
        all_rows=True,
        **data
    )

async def repo_get_roles(conn,**data):
    return await execute_function(
        "fn_obtener_rol_por_codigo_usuario",
        "Rol encontrado correctamente",
        conn,
        **data
    )