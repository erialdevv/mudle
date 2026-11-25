from repositories.general.util import execute_function

async def repo_get_permissions_by_rolid(conn, **data) -> dict:
    return await execute_function(
        "fn_obtener_permisos_por_rol_id",
        "Consulta de permisos realizada correctamente",
        conn,
        **data
    )