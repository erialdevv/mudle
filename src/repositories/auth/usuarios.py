from sqlalchemy import text


async def insertar_usuario(conn, **datos):
    
    try:
        parametros = ", ".join([f":{clave}" for clave in datos.keys()])
        print(parametros)
        lcsql = text(f"CALL sp_insertar_usuario({parametros})")
        
        await conn.execute(lcsql, datos)
        
        return{"estado":True, "msg":"Usuario insertado correctamente"}
        
    except Exception as error:
        return{"estado":False, "msg":str(error)}
    
    