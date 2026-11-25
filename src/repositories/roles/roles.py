from repositories.general.util import execute_sp

async def repo_insert_roles(conn,**data):
    return await execute_sp(
        "sp_insertar_rol",
        "Rol creado exitosamente",
        conn,
        **data
    )