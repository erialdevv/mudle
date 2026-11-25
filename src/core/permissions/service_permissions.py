from core.permissions.permission_cache import get_role_permissions
from db.redis_client import redis_client
from fastapi import Depends
from core.security.token import validate_acces_token
from db.connection import DbConn
from core.permissions.bitmask_engine import SystemModules,ActionsPermissions,check_permission
from core.general.errors import UnauthorizedError

from fastapi import Depends, HTTPException, status

def validate_permissions(
    module_required: SystemModules,
    mask_required: ActionsPermissions
):
    async def _dependency(
        conn: DbConn,
        token_data: dict = Depends(validate_acces_token),
    ) -> dict:
        
        rolid: int = token_data.get("rol_id")
        # Obtienes los permisos reales desde Redis o BD
        perm_data: dict = await get_role_permissions(redis_client, conn, rolid)
        version_perm: int = perm_data["vers_rol"]
        
        if token_data["version"] != version_perm:
            raise UnauthorizedError("Los permisos de tu rol cambiaron; renueva la sesión.")
        
        
        
        map_mask_bits: dict = perm_data["mask_bits"]

        # Máscara de usuario para el modulo requerido
        user_mask = map_mask_bits.get(module_required, 0)
        
        resultado: bool = check_permission(user_mask, mask_required)
        
        if not resultado:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta acción"
            )
            
        # Puedes devolver token_data si quieres reutilizarlo en el endpoint
        return token_data

    return _dependency
