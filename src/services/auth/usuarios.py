from core.security.password import hash_contrasena
from fastapi import Request
from repositories.auth.usuarios import repo_insertar_usuario,repo_actualizar_usuario
from models.auth.usuarios import Usuarios
s

async def servicio_guardar_usuario(conn,dominios_permitidos,**datos):
    try:
        contrasena = datos.get("contrasena")
    
        if not contrasena:
            return{"estado":False, "msg":"La contrasena es un campo requerido."}
        
        email=datos.get("email_est")
        if not email:
            return{"estado":False, "msg":"El email es un campo es requerido."}
        
        contrasena_hash=hash_contrasena(contrasena)
        
        usuario_dominio = Usuarios(
            creado_por=datos.get("p_creado_por"),
            pcid=datos.get("p_pcid"),
            contrasena=contrasena_hash,
            email=datos.get("email_est"),
            dominios_permitidos=dominios_permitidos,
            nombre=datos.get("nombre"),
            apellido=datos.get("apellido")
        )
        
        parametros_sp = {
            "p_contrasena": usuario_dominio.contrasena,
            "p_email_est": usuario_dominio.email,
            "p_creado_por": usuario_dominio.creado_por,
            "p_pcid": usuario_dominio.pcid,
            "p_nombre": usuario_dominio.nombre,
            "p_apellido": usuario_dominio.apellido
        }

        #aqui se encontrar errores de la ejecucion del sp
        resultado:dict=await repo_insertar_usuario(conn, **parametros_sp)
        
        return resultado
                    
    except ValueError as val_error:
        return {"estado": False, "msg": str(val_error)}
    except Exception as error:
        #aqui se receptan los errores por si la conexion fallo o errores de la manipulacion de colecciones
        return {"estado":False, "msg":f"Error en la conexión: {str(error)}"}
    
async def servicio_actualizar_usuario(conn,dominios_permitidos,**datos:dict):
    try:
        if datos.get("codigo") is None or datos.get("codigo") == "":
            return {"estado": False, "msg": "No se puede continuar sin el codigo del usuario."}
        
        n_parametros=len(datos)-1
        
        hipotesis1=list(datos.values()).count(None)
        
        if hipotesis1==n_parametros:
            return{"estado":False, "msg":"Todos los campos exceptuando el codigo estan vacios"}
        
        if datos.get("contrasena"):
            contrasena_hash=hash_contrasena(datos["contrasena"])
            
                        
    
        usuario=Usuarios(
            editado_por=datos.get("p_editado_por"),
            pcid=datos.get("p_pcid"),
            contrasena=contrasena_hash,
            email=datos.get("email_est"),
            dominios_permitidos=dominios_permitidos if datos.get("email_est") else None,
            nombre=datos.get("nombre"),
            apellido=datos.get("apellido")
        )
        
        parametros_sp:dict={
            "p_codigo":usuario.codigo,
            "p_nombre":usuario.nombre,
            "p_apellido":usuario.apellido,
            "p_email_est":usuario.email,
            "p_contrasena":usuario.contrasena,
        }
        
        resultado:dict=repo_actualizar_usuario(conn,**parametros_sp)
        
        return resultado
        
    except ValueError as error:
        return {"estado": False, "msg": str(error)}
    except Exception as error:
        return {"estado":False, "msg":f"Error en la conexión: {str(error)}"}
    