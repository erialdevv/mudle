from argon2 import PasswordHasher

ph = PasswordHasher()

def hash_contrasena(contrasena:str):
    return ph.hash(contrasena)

def verificar_contrasena(contrasena, hash_bd):
    try:
        ph.verify(hash_bd, contrasena)
        return{
            "estado":True,
            "msg":"Contraseña verificada exitosamente."
        }
    except Exception as error:
        return{
            "estado":True,
            "msg":"Contraseña incorrecta."
        }