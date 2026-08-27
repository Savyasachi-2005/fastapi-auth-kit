import uuid
from datetime import datetime

from pydantic import BaseModel,EmailStr,Field

class UserCreate(BaseModel):
    email:EmailStr
    password: str=Field(min_length=8,max_length=121)

class UserRead(BaseModel):
    id:uuid.UUID
    email:EmailStr
    is_active:bool
    is_verified:bool
    created_at:datetime

    model_config={
        "from_attributes":True
    }

class LoginRequest(BaseModel):
    email:EmailStr
    password:str=Field(min_length=8,max_length=121)
class TokenResponse(BaseModel):
    access_token:str
    refresh_token:str|None=None
    token_type:str="Bearer"
    csrf_token:str|None=None

class RefreshRequest(BaseModel):
    refresh_token:str

class RequestVerifyEmail(BaseModel):
    email:EmailStr

class MessageResponse(BaseModel):
    message:str

class ForgotPasswordRequest(BaseModel):
    email:EmailStr

class ResetPasswordRequest(BaseModel):
    token:str
    new_password:str=Field(min_length=8,max_length=121)
