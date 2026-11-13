from sqlalchemy import text

async def repo_valid_login(conn, email: str) -> dict | None:
    sql = text("""
        SELECT 
            id, 
            codigo, 
            nombre, 
            contrasena
        FROM sis_usuarios
        WHERE LOWER(email_est) = LOWER(:email)
          AND anulado = FALSE
        LIMIT 1
    """)
    
    result = await conn.execute(sql, {"email": email})
    user = result.mappings().first()
    
    return dict(user) if user else None
