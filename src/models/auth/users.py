from models.base_entity import BaseEntity
import uuid
from datetime import datetime
from email_validator import validate_email, EmailNotValidError


def verify_email(email: str, check_domain: bool = False, allowed_domains: list[str] | None = None) -> dict:
    
    if allowed_domains is None:
        allowed_domains = []

    if not email or not email.strip():
        return {
            "status": False,
            "msg": "Please enter an email address."
        }
    
    try:
        response = validate_email(email, check_deliverability=check_domain)
        
        if check_domain:
            if response.domain not in allowed_domains:
                return {
                    "status": False,
                    "msg": f"The domain '{response.domain}' is not allowed."
                }
        return {
            "status": True,
            "msg": "The email address was validated successfully."
        }
        
    except EmailNotValidError as error:
        return {
            "status": False,
            "msg": f"The email address is not valid: {str(error)}."
        }

    
def verify_length(value:str|None):
    if value and value.strip():
        if len(value)>150:
            return{
                "status":False,
                "msg":"The referenced field exceeded the allowed character limit."
            }
    else:
        return{
            "status":False,
            "msg":"The entered field is empty."
        }
    return{
        "status":True,
        "msg":"Validation successful."
    }


class User(BaseEntity):
    
    def __init__(
        self,
        pcid: str,
        password:str|None=None,
        email:str=None, # email institucional
        allowed_domains:list[str]=None,
        id:int=None,
        code:uuid.UUID=None,
        first_name:str=None,
        last_name:str=None,
        voided: bool = False, # False como valor inicial
        created_at: datetime = None,
        edited_at: datetime = None,
        edited_by: str = None,
        created_by: str=None,
    ):
        super().__init__(
            id=id,
            code=code,
            created_by=created_by,
            pcid=pcid,
            voided=voided,
            created_at=created_at,
            edited_at=edited_at,
            edited_by=edited_by
        )
        self.password=password
        self.email=email
        self.first_name=first_name
        self.last_name=last_name
        
        if email!=None:
            email_check:dict= verify_email(
                self.email, check_domain=True, 
                allowed_domains=allowed_domains
            )
            
            if not email_check["status"]:
                raise ValueError(f"[EMAIL]: {email_check['msg']}")
        
        if first_name!=None:
            first_name_check:dict=verify_length(self.first_name)
            if not first_name_check["status"]:
                raise ValueError(f"[FIRST_NAME]: {first_name_check['msg']}")
        
        if last_name!=None:
            last_name_check:dict=verify_length(self.last_name)
            if not last_name_check["status"]:
                raise ValueError(f"[LAST_NAME]: {last_name_check['msg']}")
