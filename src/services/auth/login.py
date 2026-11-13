from core.security.password import verify_password
from repositories.auth.login import repo_valid_login
from core.security.token import create_token

async def service_login(conn,**data):
    #En este punto, email y password, viene llena gracias a pydantic
    try:
        email:str=data["email"]
        password:str=data["password"]
        
        user_valid:dict|None=await repo_valid_login(conn,email)
        
        if not user_valid:
            return{"status":False,"msg":"Usuario inexistente o email incorrecto." }
        
        if not (user_valid.get("contrasena")):
            return{"status":False,"msg":f"La bd no arroja datos de contrasena para este usuario: {user_valid["nombre"]}"}
        
        resultado:dict=verify_password(password,user_valid.get("contrasena"))
        
        if resultado["status"]:
            token = create_token(user_valid["codigo"], user_valid["nombre"])
            return{
                "status":True,
                "msg":"Inicio de sesión completado exitosamente.",
                "detail":{
                    "user_id":user_valid["id"],
                    "token":token
                }
            }
        else:
            return{
                "status":False,
                "msg":resultado["msg"]
            }
  
    except ValueError as val_error:
        return {"status": False, "msg": str(val_error)}
    except Exception as error:
        return {"status": False, "msg": f"Connection error: {str(error)}"}
    


    
    
    