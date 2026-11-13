from sqlalchemy import text


async def execute_sp(statement,msg:str,conn,**data):
    
        parameters = ", ".join([f":{key}" for key in data.keys()])
        sql = text(f"CALL {statement}({parameters})")
        print(sql)
        await conn.execute(sql, data)
        
        return{"status":True, "msg":msg}
        
        
async def repo_insert_user(conn, **data):
    
    return await execute_sp(
        "sp_insertar_usuario", 
        "User inserted successfully",
        conn, 
        **data
    )

async def repo_update_user(conn, **data):
    return await execute_sp(
        "sp_actualizar_usuario", 
        "User updated successfully",
        conn, 
        **data)
