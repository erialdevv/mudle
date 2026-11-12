import uuid
from datetime import datetime


def validar_uuid(id_a_validar:str|uuid.UUID, version: int = 4) -> dict: 
    """
    Usado para también verificar IDs de campos de auditoría (creadopor y editadopor).
    Valida un UUID válido.
    Entrega un diccionario con 'estado' y 'msg' como llaves.
    """
    
    def validar_version(objeto_uuid:uuid.UUID, version_interna:int=version):
        if objeto_uuid.version==version_interna:
            return {"estado": True, "msg": "Validación exitosa."}
        else:
            return {"estado": False, "msg": "Uuid valido, sin embargo la version es incorrecta"}
    
    if isinstance(id_a_validar,uuid.UUID):
        return validar_version(id_a_validar)
    
    if isinstance(id_a_validar,str):
        try:
            objeto_uuid=uuid.UUID(id_a_validar)
            return validar_version(objeto_uuid)
        except ValueError:
            return {
                "estado": False, 
                "msg": f"El identificador '{id_a_validar}' no tiene un formato de UUID válido."
            }
    return {
        "estado":False,
        "msg": f"Tipo de dato '{type(id_a_validar).__name__}' no es válido para validación."
    }
        
def validar_pcid(cadena:str)->dict:
    
    if not(cadena.strip()):
        return{
            "estado":False,
            "msg":"Campo PcID vacio, porfavor ingrese uno antes de continuar"
        }
    
    if len(cadena)>150:
        return{
            "estado":False,
            "msg":"Desbordamiento de caracteres"
        }
    
    return {"estado":True,"msg":"Validacion exitosa"}

def validar_estado(estado:bool):
    if estado is None or not isinstance(estado, bool):
        return{
            "estado":False,
            "msg":"El estado no puede estar vacío y debe ser un valor booleano (True o False)."
        }

    return{
        "estado":True,
        "msg":"Validacion exitosa"
    }

class BaseEntidades:
    
    def __init__(
        self,
        codigo:uuid.UUID,
        pcid: str,
        anulado: bool = False, # False como valor inicial
        id:int|None=None,
        fecha_creacion: datetime|None = None,
        fecha_editado: datetime|None = None,
        editado_por: str|None= None,
        creado_por: str|None=None,
    ):
        self.id = id
        self.codigo=codigo
        self.anulado = anulado
        self.creado_por =creado_por 
        self.editado_por = editado_por
        self.pcid = pcid
        self.fecha_creacion = fecha_creacion
        self.fecha_editado = fecha_editado
        
        if creado_por!=None:
            verificacion_creadopor = validar_uuid(self.creado_por)
            if not verificacion_creadopor["estado"]:
                raise ValueError("[CREADO_POR:]",verificacion_creadopor["msg"])
        
        if editado_por!=None:
            verificacion_editadopor = validar_uuid(self.editado_por)
            if not verificacion_editadopor["estado"]:
                raise ValueError("[EDITADO_POR:]",verificacion_editadopor["msg"])
        
        verificacion_pcid=validar_pcid(self.pcid)
        if not verificacion_pcid["estado"]:
            raise ValueError("[PCID: ]",verificacion_pcid["msg"])
        
        verificacion_anulado=validar_estado(self.anulado)
        if not verificacion_anulado["estado"]:
            raise TypeError("[ANULADO:]",verificacion_anulado["msg"])
        


