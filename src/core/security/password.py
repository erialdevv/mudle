from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from db.config import HashConfig

ph = PasswordHasher(time_cost=HashConfig.time_cost, memory_cost=HashConfig.memory_cost, parallelism=HashConfig.parallelism)

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
