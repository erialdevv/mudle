from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from db.config import time_cost_env, memory_cost_env, parallelism_env

ph = PasswordHasher(time_cost=time_cost_env, memory_cost=memory_cost_env, parallelism=parallelism_env)

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(password: str, db_hash: str) -> dict:
    try:
        ph.verify(db_hash, password)
        return {
            "status": True,
            "msg": "Password verified successfully."
        }
    except VerifyMismatchError:
        return {
            "status": False,
            "msg": "Incorrect password or user."
        }
    except Exception:
        return {
            "status": False,
            "msg": "Authentication error."
        }
