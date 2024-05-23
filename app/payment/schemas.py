import uuid
from datetime import datetime
from pydantic import BaseModel

from app.user import schemas as user_schemas
from app.invoice import schemas as invoice_schemas

class PaymentBase(BaseModel):
    '''Payment pydantic base model'''
    
    id: uuid.UUID
    amount_paid: float
    payment_date: datetime
    invoice: invoice_schemas.InvoiceBase
    customer: user_schemas.CustomerBase
    vendor: user_schemas.VendorBase
    

class PaymentResponse(PaymentBase):
    '''Payment pydantic base model'''
    
    class Config:
        orm_mode = True