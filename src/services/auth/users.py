from core.security.password import hash_password
from fastapi import Request
from repositories.auth.users import repo_insert_user,repo_update_user
from models.auth.users import User


async def service_save_user(conn, allowed_domains, **data):
    try:
        password_hash = hash_password(data["password"])
        
        domain_user = User(
            created_by=data.get("created_by"),
            pcid=data.get("pcid"),
            password=password_hash,
            email=data["institutional_email"],
            allowed_domains=allowed_domains,
            first_name=data["first_name"],
            last_name=data["last_name"]
        )
        
        sp_parameters = {
            "p_contrasena": domain_user.password,
            "p_email_est": domain_user.email,
            "p_creado_por": domain_user.created_by,
            "p_pcid": domain_user.pcid,
            "p_nombre": domain_user.first_name,
            "p_apellido": domain_user.last_name
        }

        return await repo_insert_user(conn, **sp_parameters)
                    
    except ValueError as val_error:
        return {"status": False, "msg": str(val_error)}
    except Exception as error:
        return {"status": False, "msg": f"Connection error: {str(error)}"}

    
async def service_update_user(conn, allowed_domains, **data: dict):
    try:
        password = data.get("password")
        password_hash = hash_password(password) if password else None

        user = User(
            edited_by=data.get("edited_by"),
            code=data["code"],
            pcid=data.get("pcid"),
            password=password_hash,
            email=data.get("institutional_email"),
            allowed_domains=allowed_domains if data.get("institutional_email") else None,
            first_name=data.get("first_name"),
            last_name=data.get("last_name")
        )

        sp_parameters: dict = {
            "p_codigo": user.code,
            "p_editado_por": user.edited_by,
            "p_nombre": user.first_name,
            "p_apellido": user.last_name,
            "p_email_est": user.email,
            "p_contrasena": user.password
        }

        return await repo_update_user(conn, **sp_parameters)

    except ValueError as error:
        return {"status": False, "msg": str(error)}
    except Exception as error:
        return {"status": False, "msg": f"Connection error: {str(error)}"}

