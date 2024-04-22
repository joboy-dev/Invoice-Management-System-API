from typing import Optional
from pydantic import BaseModel

from app.user.models import Role


class UserSchema(BaseModel):
    '''Users pydantic schema'''
    
    email: str
    password: str
    first_name: str
    last_name: str
    profile_pic: Optional[bytes]
    role: Role = Role.customer
    is_verified: bool = False
    is_active: bool = True
    

class CustomerSchema(BaseModel):
    '''Customers pydantic schema'''
    
    phone_number: str
    billing_address: str