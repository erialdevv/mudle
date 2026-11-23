from pydantic import BaseModel, Field, field_validator
from core.permissions.bitmask_engine import EnumModules


class RoleRequest(BaseModel):
    p_nombre: str
    p_version: int = 1
    p_permissions: dict[EnumModules, int] = Field(
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
    def validate(cls, perm: dict[EnumModules, int]) -> dict[EnumModules, int]:
        for module, bitmask in perm.items():
            if module not in EnumModules or bitmask < 0:
                raise ValueError(
                    f"Módulo o bitmask inválido ('{module}': {bitmask}). Módulos permitidos: {', '.join(EnumModules)} (valores >= 0)."
                )
        return perm
