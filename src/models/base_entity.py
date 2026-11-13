import uuid
from datetime import datetime


def validate_uuid(id_to_validate:str|uuid.UUID, version: int = 4) -> dict: 
    """
    Usado para también verificar IDs de campos de auditoría (creadopor y editadopor).
    Valida un UUID válido.
    Entrega un diccionario con 'estado' y 'msg' como llaves.
    """
    
    def validate_version(uuid_object:uuid.UUID, inner_version:int=version):
        if uuid_object.version==inner_version:
            return {"status": True, "msg": "Validation successful."}
        else:
            return {"status": False, "msg": "Valid UUID, but the version is incorrect."}
    
    if isinstance(id_to_validate,uuid.UUID):
        return validate_version(id_to_validate)
    
    if isinstance(id_to_validate,str):
        try:
            uuid_object=uuid.UUID(id_to_validate)
            return validate_version(uuid_object)
        except ValueError:
            return {
                "status": False, 
                "msg": f"The identifier '{id_to_validate}' does not have a valid UUID format."
            }
    return {
        "status":False,
        "msg": f"Data type '{type(id_to_validate).__name__}' is not valid for validation."
    }
        
def validate_pcid(text:str)->dict:
    
    if not(text.strip()):
        return{
            "status":False,
            "msg":"PcID field is empty, please enter one before continuing."
        }
    
    if len(text)>150:
        return{
            "status":False,
            "msg":"Character limit exceeded."
        }
    
    return {"status":True,"msg":"Validation successful."}

def validate_status(status:bool):
    if status is None or not isinstance(status, bool):
        return{
            "status":False,
            "msg":"The status cannot be empty and must be a boolean value (True or False)."
        }

    return{
        "status":True,
        "msg":"Validation successful."
    }

class BaseEntity:
    
    def __init__(
        self,
        code:uuid.UUID,
        pcid: str,
        voided: bool = False, # False como valor inicial
        id:int|None=None,
        created_at: datetime|None = None,
        edited_at: datetime|None = None,
        edited_by: str|None= None,
        created_by: str|None=None,
    ):
        self.id = id
        self.code=code
        self.voided = voided
        self.created_by =created_by 
        self.edited_by = edited_by
        self.pcid = pcid
        self.created_at = created_at
        self.edited_at = edited_at
        
        if created_by!=None:
            created_by_check = validate_uuid(self.created_by)
            if not created_by_check["status"]:
                raise ValueError("[CREATED_BY:]",created_by_check["msg"])
        
        if edited_by!=None:
            edited_by_check = validate_uuid(self.edited_by)
            if not edited_by_check["status"]:
                raise ValueError("[EDITED_BY:]",edited_by_check["msg"])
        
        pcid_check=validate_pcid(self.pcid)
        if not pcid_check["status"]:
            raise ValueError("[PCID: ]",pcid_check["msg"])
        
        voided_check=validate_status(self.voided)
        if not voided_check["status"]:
            raise TypeError("[VOIDED:]",voided_check["msg"])
