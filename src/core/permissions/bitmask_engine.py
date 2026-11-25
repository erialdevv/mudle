from enum import IntFlag, StrEnum

class ActionsPermissions(IntFlag):
    PERM_NONE    = 0  #SIN PERMISOS
    PERM_READ    = 1  #LECTURA
    PERM_CREATE  = 2  #INSERCION
    PERM_UPDATE  = 4  #ACTUALIZACION
    PERM_DELETE  = 8  #BORRAR
    PERM_EXPORT  = 16 #EXPORTAR
    
class SystemModules(StrEnum):
    AUTH="auth"
    USER="users"
    ROLES="roles"

def check_permission(user_mask:int, required_mask:int)->bool:
    
    if required_mask<=0 or user_mask<0:
        return False
    
    return (user_mask & required_mask)==required_mask

