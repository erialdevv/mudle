from sqlalchemy import text


async def ejecutar_sp(sentencia,msg:str,conn,**datos):
        parametros = ", ".join([f":{clave}" for clave in datos.keys()])
        lcsql = text(f"CALL {sentencia}({parametros})")
        
        await conn.execute(lcsql, datos)
        
        return{"estado":True, "msg":msg}
        
        
async def repo_insertar_usuario(conn, **datos):
    
    return await ejecutar_sp(
        "sp_insertar_usuario", 
        "Usuario insertado exitosamente",
        conn, 
        **datos
    )

async def repo_actualizar_usuario(conn, **datos):
    return await ejecutar_sp(
        "sp_actualizar_usuario", 
        "Usuario actualizado exitosamente",
        conn, 
        **datos)
    
        