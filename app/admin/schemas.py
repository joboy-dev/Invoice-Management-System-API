from datetime import datetime, timedelta
from typing import Optional
import uuid
from pydantic import BaseModel, EmailStr

from app.invoice.models import Status
from app.user.models import Role

class AdminUserBase(BaseModel):
    '''Admin user pydantic schema'''
    
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: Role
    is_verified: bool
    is_active: bool
    

class AdminCustomerBase(BaseModel):
    '''Admin customer pydantic schema'''
    
    phone_number: str
    billing_address: str
    user_id: uuid.UUID | None
    

class AdminVendorBase(BaseModel):
    '''Admin vendor pydantic schema'''
    
    phone_number: str
    address: str
    business_name: str
    user_id: uuid.UUID
    

# ---------------------------------------------------------------
# ---------------------------------------------------------------

class AdminProductBase(BaseModel):
    '''Admin products pydantic base schema'''
    
    name: str
    description: str
    unit_price: float
    vendor_id: uuid.UUID

# ---------------------------------------------------------------
# ---------------------------------------------------------------


class AdminInvoiceBase(BaseModel):
    '''Invoice pydantic base model'''
    
    due_date: datetime = datetime.now() + timedelta(days=7)
    status: Status = Status.pending
    customer_id: uuid.UUID
    vendor_id: uuid.UUID
    

class AdminInvoiceItemBase(BaseModel):
    '''Invoice item base schema'''
    
    description: str
    quantity: int
    tax: float
    discount: float
    additional_charges: float
    invoice_id: uuid.UUID
    product_id: uuid.UUID
    