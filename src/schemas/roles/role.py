from pydantic import BaseModel, Field, field_validator
from core.permissions.bitmask_engine import SystemModules
from schemas.general.responses import BaseResponse

class RoleRequest(BaseModel):
    p_nombre: str
    p_version: int = 1
    p_permissions: dict[SystemModules, int] = Field(
        ...,
        description="Diccionario cuya clave representa el modulo y el valor la mascara de bits",
        examples=[
            {
                "auth": 1,
                "users": 15,
            }
        ],
    )

    @field_validator("p_permissions")
    @classmethod
    def validate(cls, perm: dict[SystemModules, int]) -> dict[SystemModules, int]:
        for module, bitmask in perm.items():
            if module not in SystemModules or bitmask < 0:
                raise ValueError(
                    f"Módulo o bitmask inválido ('{module}': {bitmask}). Módulos permitidos: {', '.join(SystemModules)} (valores >= 0)."
                )
        return perm
