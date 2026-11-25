from models.base_entity import BaseEntity
import uuid
from datetime import datetime
import json

def verify_length(value:str|None):
    if value and value.strip():
        if len(value)>150:
            return{
                "status":False,
                "msg":"El campo excedió el límite de caracteres permitido."
            }
    else:
        return{
            "status":False,
            "msg":"El campo ingresado está vacío."
        }
    return{
        "status":True,
        "msg":"Validación exitosa."
    }

class Role(BaseEntity):
    
    def __init__(
        self,
        pcid: str,
        permissions:dict,
        role_id:int=None,
        code:uuid.UUID=None,
        name:str=None,
        version:int=None,
        voided: bool = False, # False como valor inicial
        created_at: datetime = None,
        edited_at: datetime = None,
        edited_by: str = None,
        created_by: str=None,
    ):
        super().__init__(
            entity_id=role_id,
            code=code,
            created_by=created_by,
            pcid=pcid,
            voided=voided,
            created_at=created_at,
            edited_at=edited_at,
            edited_by=edited_by
        )
        
        self.name=name
        self.version=version
        self.permissions=permissions
        
        if name!=None:
            name_check:dict=verify_length(self.name)
            if not name_check["status"]:
                raise ValueError(f"[NAME]: {name_check['msg']}")
        
        if version!=None:
            if self.version<=0:
                raise ValueError(f"[VERSION]: La version del rol ingresada debe ser mayor a 0")
            
        if permissions!=None:
            self.permissions=json.dumps(permissions)