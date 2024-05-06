from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, EmailStr

from app.user.models import Role

class UserBase(BaseModel):
    '''Users pydantic schema'''
    
    username: str
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
    
    id: uuid.UUID
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    profile_pic: Optional[bytes]
    role: Role
    # created_at: datetime
    # is_verified: bool
    # is_active: bool
    
    class Config:
        orm_mode = True
    

class CreateUser(BaseModel):
    '''Schema to create user'''
    
    username: str
    email: EmailStr
    password: str
    password2: str
    first_name: str
    last_name: str
    role: Role = Role.customer
    
    
class LoginUser(BaseModel):
    '''Schema to login a user'''
    
    username: str
    password: str
    

class UpdateDetails(BaseModel):
    '''Schema to update user details'''
    
    username: str
    first_name: str
    last_name: str


class UpdateEmail(BaseModel):
    '''Schema to update user email'''
    
    email: EmailStr
    

class ReveifyEmail(UpdateEmail):
    pass
    
    
class ChangePassword(BaseModel):
    '''Schema to change user password'''
    
    email: EmailStr
    old_password: str
    new_password: str
    password2: str


# -------------------------------------------------------
# -------------------------------------------------------

class Token(BaseModel):
    '''Schema for access token'''
    
    access_token: str
    token_type: str
    

class TokenData(BaseModel):
    '''Schema to structure token data'''
    
    id: Optional[uuid.UUID]
    

# -------------------------------------------------------
# -------------------------------------------------------


class CustomerBase(BaseModel):
    '''Customers pydantic schema'''
    
    id: uuid.UUID
    phone_number: str
    billing_address: str
    

class CustomerResponse(BaseModel):
    '''Customers pydantic response schema'''
    
    id: uuid.UUID
    phone_number: str
    billing_address: str
    user: UserResponse
    
    class Config:
        orm_mode = True
    

class CreateCustomer(CustomerBase):
    '''Schema to create a new customer'''
    
    pass


class UpdateCustomer(CustomerBase):
    '''Schema to update a customer profile'''
    
    pass


# -------------------------------------------------------
# -------------------------------------------------------


class VendorBase(BaseModel):
    '''Vendors pydantic schema'''
    
    phone_number: str
    address: str
    business_name: str
    business_pic: Optional[bytes] | None = None
    

class VendorResponse(BaseModel):
    '''Vendors pydantic response schema'''
    
    id: uuid.UUID
    address: str
    business_name: str
    business_pic: Optional[bytes] | None
    user: UserResponse
    
    class Config:
        orm_mode = True
        
    
class CreateVendor(VendorBase):
    '''Schema to create a new vendor prifile'''
    
    pass


class UpdateVendor(VendorBase):
    '''Schema to update a vendor profile'''
    
    pass
