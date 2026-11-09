from models.entidad_base import BaseEntidades
import uuid
from datetime import datetime
from email_validator import validate_email, EmailNotValidError


def verificar_email(email: str, check_dominio: bool = False, dominios_permitidos: list[str] | None = None) -> dict:
    
    if dominios_permitidos is None:
        dominios_permitidos = []

    if not email or not email.strip():
        return {
            "estado": False,
            "msg": "Por favor, ingrese una dirección de correo electrónico."
        }
    
    try:
        respuesta = validate_email(email, check_deliverability=check_dominio)
        
        if check_dominio:
            if respuesta.domain not in dominios_permitidos:
                return {
                    "estado": False,
                    "msg": f"El dominio '{respuesta.domain}' no está permitido."
                }
        return {
            "estado": True,
            "msg": "El correo electrónico ha sido validado correctamente."
        }
        
    except EmailNotValidError as error:
        return {
            "estado": False,
            "msg": f"La dirección de correo no es válida: {str(error)}."
        }

    
def verifacion_longitudes(valor:str|None):
    if valor and valor.strip():
        if len(valor)>150:
            return{
                "estado":False,
                "msg":"EL campo referenciado ha superado el limite de caracteres permitido."
            }
    else:
        return{
            "estado":False,
            "msg":"El campo ingresado esta vacio."
        }
    return{
        "estado":True,
        "msg":"Validacion exitosa."
    }


class Usuarios(BaseEntidades):
    
    def __init__(
        self,
        creado_por: str,
        pcid: str,
        contrasena:str,
        email:str, # email institucional
        id:int=None,
        codigo:uuid.UUID=None,
        nombre:str=None,
        apellido:str=None,
        anulado: bool = False, # False como valor inicial
        fecha_creacion: datetime = None,
        fecha_editado: datetime = None,
        editado_por: str = None,
    ):
        super().__init__(
            id=id,
            codigo=codigo,
            creado_por=creado_por,
            pcid=pcid,
            anulado=anulado,
            fecha_creacion=fecha_creacion,
            fecha_editado=fecha_editado,
            editado_por=editado_por
        )
        self.contrasena=contrasena
        self.email=email
        self.nombre=nombre
        self.apellido=apellido
        
        verificacion_email:bool|str= verificar_email(self.email)
        if not verificacion_email["estado"]:
            raise ValueError(f"[EMAIL]: {verificacion_email['msg']}")
        
        verifacion_nombre:bool|str=verifacion_longitudes(self.nombre)
        if not verifacion_nombre["estado"]:
            raise ValueError(f"[NOMBRE]: {verifacion_longitudes["msg"]}")
        
        verificacion_apellido:bool|str=verifacion_longitudes(self.apellido)
        if not verificacion_apellido["estado"]:
            raise ValueError(f"[APELLIDO]: {verifacion_longitudes["msg"]}")


    
        
        