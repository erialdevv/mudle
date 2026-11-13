import uuid
from typing import Annotated
from pydantic import BaseModel, EmailStr, StringConstraints, field_validator,model_validator


NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

class CreateUserRequest(BaseModel):
    first_name: NonEmptyStr
    last_name: NonEmptyStr
    institutional_email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("The password is a required field.")
        return v

class ReadUserResponse(BaseModel):
    code:uuid.UUID
    first_name:str
    last_name:str
    institutional_email:EmailStr
    voided:bool

class UpdateUserRequest(BaseModel):
    
    code: uuid.UUID
    first_name: NonEmptyStr | None = None
    last_name: NonEmptyStr | None = None
    institutional_email: EmailStr | None = None
    password: str | None = None

    @field_validator("password")
    @classmethod
    def password_not_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Password cannot be empty or whitespace.")
        return v

    @model_validator(mode="after")
    def at_least_one_field_to_update(self):
        updatable_fields = (
            self.first_name,
            self.last_name,
            self.institutional_email,
            self.password,
        )
        if all(field is None for field in updatable_fields):
            raise ValueError("All fields except the code are empty.")
        return self


class UpdateMultipleUsersRequest(BaseModel):
    user_ids: list[int]  # Lista de IDs de los usuarios a modificar
    first_name: str | None = None
    last_name: str | None = None
    institutional_email: EmailStr | None = None
    password: str | None = None

class VoidUserRequest(BaseModel):
    voided:bool

class VoidMultipleUsersRequest(BaseModel):
    user_ids: list[int]  # Lista de IDs de los usuarios a modificar
    first_name: str | None = None
    last_name: str | None = None
    institutional_email: EmailStr | None = None
    password: str | None = None
