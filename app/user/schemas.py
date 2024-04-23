from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

from app.user.models import Role


class UserBase(BaseModel):
    '''Users pydantic schema'''
    
    email: EmailStr
    password: str
    password2: str
    first_name: str
    last_name: str
    profile_pic: Optional[bytes]
    role: Role = Role.customer
    is_verified: bool = False
    is_active: bool = True
    

class UserResponse(BaseModel):
    '''Users pydantic response schema'''
    
    email: EmailStr
    first_name: str
    last_name: str
    profile_pic: Optional[bytes]
    role: Role = Role.customer
    created_at: datetime
    
    class Config:
        orm_mode = True
    

class CreateUser(BaseModel):
    '''Schema to create user'''
    
    email: EmailStr
    password: str
    password2: str
    first_name: str
    last_name: str
    role: Role = Role.customer
    
    
class LoginUser(BaseModel):
    '''Schema to login a user'''
    
    email: EmailStr
    password: str


class UpdateEmail(BaseModel):
    '''Schema to update user email'''
    
    email: EmailStr
    
    
class ChangePassword(BaseModel):
    '''Schema to change user password'''
    
    email: EmailStr
    old_password: str
    new_password: str
    password2: str
    

class UploadProfilePicture(BaseModel):
    '''Schema to update profile picture'''
    
    profile_pic: Optional[bytes]


# -------------------------------------------------------
# -------------------------------------------------------

class CustomerBase(BaseModel):
    '''Customers pydantic schema'''
    
    phone_number: str
    billing_address: str
    

class CustomerBase(BaseModel):
    '''Customers pydantic response schema'''
    
    phone_number: str
    billing_address: str
    
    class Config:
        orm_mode = True
    

class CreateCustomer(CustomerBase):
    '''Schema to create a new customer'''
    
    pass