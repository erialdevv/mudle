from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from db.config import time_cost_env, memory_cost_env, parallelism_env

ph = PasswordHasher(time_cost=time_cost_env, memory_cost=memory_cost_env, parallelism=parallelism_env)

def hash_contrasena(contrasena: str) -> str:
    return ph.hash(contrasena)

def verificar_contrasena(contrasena: str, hash_bd: str) -> dict:
    try:
        ph.verify(hash_bd, contrasena)
        return {
            "estado": True,
            "msg": "Contraseña verificada exitosamente."
        }
    except VerifyMismatchError:
        return {
            "estado": False,
            "msg": "Contraseña o usuario incorrectos."
        }
    except Exception:
        return {
            "estado": False,
            "msg": "Error en la autenticación."
        }


