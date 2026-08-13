from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr, Field
class Role(str,Enum): STUDENT="STUDENT"; STAFF="STAFF"; ADMIN="ADMIN"
class RegisterRequest(BaseModel):
    email:EmailStr
    full_name:str=Field(min_length=2,max_length=120)
    password:str=Field(min_length=8,max_length=128)
class LoginRequest(BaseModel): email:EmailStr; password:str=Field(min_length=1,max_length=128)
class UserResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:str; email:str; full_name:str; role:str; active:bool
class LoginResponse(BaseModel): access_token:str; token_type:str="bearer"; user:UserResponse
class RoleUpdate(BaseModel): role:Role
class ActiveUpdate(BaseModel): active:bool
