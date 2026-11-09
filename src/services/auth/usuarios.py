from core.security.password import hash_contrasena
from repositories.auth.usuarios import insertar_usuario
from models.auth.usuarios import Usuarios

async def guardar_usuario(engine, **datos):
    try:
        async with engine.begin() as conn:
            
            contrasena = datos["contrasena"]
    
            if not contrasena:
                return{"estado":False, "msg":"La contrasena es requerida"}
            
            contrasena_hash=hash_contrasena(contrasena)
            
            usuario_dominio = Usuarios(
                creado_por=datos.get("p_creado_por"),
                pcid=datos.get("p_pcid"),
                contrasena=contrasena_hash,
                email=datos.get("email_est"),
                nombre=datos.get("nombre"),
                apellido=datos.get("apellido")
            )
            
            datos_para_sp = {
                "p_contrasena": usuario_dominio.contrasena,
                "p_email_est": usuario_dominio.email,
                "p_creado_por": usuario_dominio.creado_por,
                "p_pcid": usuario_dominio.pcid,
                "p_nombre": usuario_dominio.nombre,
                "p_apellido": usuario_dominio.apellido
            }
    
            #aqui se encontrar errores de la ejecucion del sp
            resultado:dict=await insertar_usuario(conn, **datos_para_sp)
            
            return resultado
                    
    except ValueError as val_error:
        return {"estado": False, "msg": str(val_error)}
    except Exception as error:
        #aqui se receptan los errores por si la conexion fallo o errores de la manipulacion de colecciones
        return {"estado":False, "msg":f"Error en la conexión: {str(error)}"}